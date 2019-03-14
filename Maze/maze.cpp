#include "Maze.h"
#include <algorithm>
#include <random>
#include <thread>
#include <chrono>

void generateBitmapImage(const std::vector< std::vector< bool > >& image,
                         int height, int width, const char* imageFileName);

//////////////////////////////////////////////////////////////

Simulation::Simulation(int w, int h) :
  width(w),
  height(h),
  InitialPos(0.0, 0.0, 0.0),
  speedl(0.0),
  speedr(0.0),
  area(w, std::vector< bool >(h, false))
{}

Corners Simulation::GetCorners(Pos p) const
{
  Corners c;
  p.Move(getRobotLength() / 2.0);
  p.Move(Angle(-PI / 2.0), getRobotWidth() / 2.0);
  c.FL = p;
  p.Move(Angle(PI / 2.0), getRobotWidth());
  c.FR = p;
  p.Move(Angle(PI), getRobotLength());
  c.BR = p;
  p.Move(Angle(-PI / 2.0), getRobotWidth());
  c.BL = p;

  return c;
}

bool Simulation::SetPixel(int x, int y, int w, bool h, bool detect)
{
  if (x < 0 || x >= (int)area.size() || y < 0 || y >= (int)(area[x].size())) {
    return false;
  }

  if (detect) return area[x][y];

  const int ex  = w / 2;
  area[x][y] = true;
  if (h) {
    for (int xx = x - ex; xx <= x + ex; ++xx) {
      if (xx >= 0 && xx < (int)area.size()) {
        area.at(xx)[y] = true;
      }
    }
  }
  else {
    for (int yy = y - ex; yy < y + ex; ++yy) {
      if (yy >= 0 && yy < (int)area.at(0).size()) {
        area[x].at(yy) = true;
      }
    }
  }

  return false;
}

bool Simulation::Line(int x1, int y1, int x2, int y2, int thick, bool detect)
{
  const bool steep = abs(y2 - y1) > abs(x2 - x1);

  if (x1 != x2 && y1 != y2) {
    thick = static_cast<int>(thick * 1.4);
  }

  const int dx = x2 - x1;
  const int dy = y2 - y1;
  const int dx1 = abs(dx);
  const int dy1 = abs(dy);
  int px = 2 * dy1 - dx1;
  int py = 2 * dx1 - dy1;

  int x, y;

  if (dy1 <= dx1) {
    int xe;
    if (dx >= 0) {
      x = x1;
      y = y1;
      xe = x2;
    }
    else {
      x = x2;
      y = y2;
      xe = x1;
    }

    if (SetPixel(x, y, thick, steep, detect)) return true;

    while (x < xe) {
      ++x;
      if (px < 0) {
        px = px + 2 * dy1;
      }
      else {
        if ((dx < 0 && dy < 0) || (dx > 0 && dy > 0)) ++y;
        else --y;
        px = px + 2 * (dy1 - dx1);
      }

      if (SetPixel(x, y, thick, steep, detect)) return true;
    }
  }
  else {
    int ye;
    if (dy >= 0) {
      x = x1;
      y = y1;
      ye = y2;
    }
    else {
      x = x2;
      y = y2;
      ye = y1;
    }

    if (SetPixel(x, y, thick, steep, detect)) return true;

    while (y < ye) {
      ++y;
      if (py <= 0) {
        py = py + 2 * dx1;
      }
      else {
        if ((dx < 0 && dy < 0) || (dx > 0 && dy > 0)) ++x;
        else --x;
        py = py + 2 * (dx1 - dy1);
      }

      if (SetPixel(x, y, thick, steep, detect)) return true;
    }
  }

  return false;
}

void Simulation::MoveRobot(double musec)
{
  std::lock_guard<std::mutex> lg(speedMutex);

  if (speedl != 0.0 || speedr != 0.0) {
    Pos P = GetRobotPos();

    P.Curve(speedl, speedr, musec / 1000.0, getTurnWidth());
    SetRobotPos(P);

    Marks.push_back({toint(P.x()), toint(P.y())});
  }
}

void Simulation::setSpeed(double left, double right)
{
  std::lock_guard<std::mutex> g(speedMutex);
  speedl = left;
  speedr = right;
}

double Simulation::getDistance(const Sensor& s)
{
  static std::random_device gen;
  static std::mt19937 mt(gen());
  static std::normal_distribution<double> normdist(3500.0, 500.0);

  const double criterion = 30.0;

  Pos p = GetRobotPos();
  s.Process(p);

  Angle alpha = p.getAngle() + s.getAngle();

  const double sina = sin(alpha);
  const double cosa = cos(alpha);

  double mindist = 0.0;
  const double maxstart = normdist(mt);
  double maxdist = maxstart;

  const double gunx = p.x();
  const double guny = p.y();

  const double tx = gunx + sina * maxdist;
  const double ty = guny + cosa * maxdist;

  if (!LineHit(gunx, guny, tx, ty))
    return -1.0;

  do {
    const double distance = (mindist + maxdist) / 2.0;
    const double px = gunx + sina * distance;
    const double py = guny + cosa * distance;

    if (LineHit(gunx, guny, px, py)) {
      maxdist = distance;
    } else {
      mindist = distance;
    }
  } while (maxdist - mindist > criterion);

  if (mindist > maxstart - criterion)
    return -1.0;

  const double distance = (mindist + maxdist) / 2.0;
  std::this_thread::sleep_for(std::chrono::milliseconds(50));
  return distance;
}

bool Simulation::crashed() 
{
  const Corners C = GetCorners(GetRobotPos());
  
  return LineHit(C.FL, C.FR) || LineHit(C.FR, C.BR) ||
         LineHit(C.BR, C.BL) || LineHit(C.BL, C.FL);
}

bool Simulation::finished()
{
  const Corners C = GetCorners(GetRobotPos());

  return !C.FL.CheckBoundary(width, height, 5.0) ||
         !C.FR.CheckBoundary(width, height, 5.0) ||
         !C.BR.CheckBoundary(width, height, 5.0) ||
         !C.BL.CheckBoundary(width, height, 5.0);
}

void Simulation::write(std::string filename, const std::vector<Point>& pvec)
{
  // Write outline of robot
  const Corners C = GetCorners(GetRobotPos());

  try { Line(C.FL, C.FR); } catch (...) {} 
  try { Line(C.FR, C.BR); } catch (...) {}
  try { Line(C.BR, C.BL); } catch (...) {}
  try { Line(C.BL, C.FL); } catch (...) {}

  // Write marks
  for (auto& p : Marks) {
    try {
      area.at(p.first).at(p.second) = true;
    } catch (...) {}
  }

  // Write obstacles
  for (auto ob : pvec) {
    ob += InitialPos;
    const int x = toint(ob.x());
    const int y = toint(ob.y());

    for (int xx = x - 2; xx < x + 3; ++xx)
    {
      if (xx >= 0 && xx < (int)area.size()) {
        for (int yy = y - 2; yy < y + 3; ++yy)
        {
          if (yy >= 0 && yy < (int)area[x].size()) {
            try {
              area[xx][yy] = !area[xx][yy];
            } catch (...) {}
          }
        }
      }
    }
  }

  generateBitmapImage(area, area.at(0).size(), area.size(), filename.c_str());
}

#ifndef WIN32
void Reality::write(std::string filename, const std::vector<Point>& pvec)
{
  int minx = 0, maxx = 0, miny = 0, maxy = 0;

  // Get range of obstacles
  for (auto ob : pvec) {
    minx = std::min(minx, (int)ob.x());
    maxx = std::max(maxx, (int)ob.x());
    miny = std::min(miny, (int)ob.y());
    maxy = std::max(maxy, (int)ob.y());
  }

  std::vector< std::vector < bool > > area(maxx - minx + 100, std::vector < bool >(maxy - miny + 100));

  // Write obstacles
  for (auto ob : pvec) {
    const int x = toint(ob.x()) - minx + 50;
    const int y = toint(ob.y()) - miny + 50;

    for (int xx = x - 2; xx < x + 3; ++xx)
    {
      if (xx >= 0 && xx < (int)area.size()) {
        for (int yy = y - 2; yy < y + 3; ++yy)
        {
          if (yy >= 0 && yy < (int)area[xx].size()) {
            area.at(xx).at(yy) = !area[xx][yy];
          }
        }
      }
    }
  }

  generateBitmapImage(area, area.at(0).size(), area.size(), filename.c_str());
}
#endif

//////////////////////////  Maze1 2018 maze  ////////////////////////

Maze1::Maze1() : Simulation(2440, 1220)
{
  const int maxx = width - 1;
  const int maxy = height - 1;
  const int wall = 35;
  const int middle = wall / 2;
  const int vpathwidth = 400;
  const int hpathwidth = 360;

  const double initialx = wall + vpathwidth / 2;       // middle of the road

  // left and right outer sides near entrance and exit
  LineInt(middle, 0, middle, maxy, wall);
  LineInt(maxx - middle, 0, maxx - middle, maxy, wall);
  // upper and lower sides
  LineInt(wall + middle + vpathwidth, middle, width, middle, wall);
  LineInt(0, height - middle, width - wall - middle - vpathwidth, height - middle, wall);

  // diagonal values
  int startx = wall + middle + vpathwidth;
  int starty = height / 2;
  int endy = height - wall - hpathwidth;
  int endx = startx + endy - starty;

  LineInt(startx, 0, startx, starty, wall);
  LineInt(startx, starty, endx, endy, wall);
  LineInt(endx, endy, width / 2, endy, wall);

  startx = width - wall - vpathwidth - middle;
  endy = wall + hpathwidth + middle;
  endx = startx + endy - starty;

  LineInt(startx, height, startx, starty, wall);
  LineInt(startx, starty, endx, endy, wall);
  LineInt(endx, endy, width / 2, endy, wall);
}

//////////////////////////  Maze2  ////////////////////////

Maze2::Maze2() : Simulation(2440, 1220)
{
  const int maxx = width - 1;
  const int maxy = height - 1;
  const int wall = 35;
  const int middle = wall / 2;

  const int numpaths = 5;
  const int pathwidth = (width - wall * (numpaths + 1)) / numpaths;

  const double initialx = wall + pathwidth / 2;  // middle of the road

  // left and right outer sides near entrance and exit
  LineInt(middle, 0, middle, maxy, wall);
  LineInt(maxx - middle, 0, maxx - middle, maxy, wall);
  // upper and lower sides
  LineInt(wall + middle + pathwidth, middle, width, middle, wall);
  LineInt(0, height - middle, width - wall - middle - pathwidth, height - middle, wall);

  int wallx = wall + pathwidth + middle;
  LineInt(wallx, 0, wallx, height - wall - pathwidth, wall);
  wallx = 3 * wall + 3 * pathwidth + middle;
  LineInt(wallx, 0, wallx, height - wall - pathwidth, wall);

  wallx = 2 * wall + 2 * pathwidth + middle;
  LineInt(wallx, wall + pathwidth, wallx, height, wall);
  wallx = 4 * wall + 4 * pathwidth + middle;
  LineInt(wallx, wall + pathwidth, wallx, height, wall);
}


//////////////////////////  Maze3  ////////////////////////

Maze3::Maze3() : Simulation(2440, 1220)
{
  const int maxx = width - 1;
  const int maxy = height - 1;
  const int wall = 20;
  const int middle = wall / 2;

  const int numpaths = 3;
  const int pathwidth = (height - wall * (numpaths + 1)) / numpaths;

  const double initialx = wall + pathwidth / 2;  // middle of the road

  // left and right outer sides near entrance and exit
  LineInt(middle, 0, middle, maxy, wall);
  LineInt(maxx - middle, 0, maxx - middle, maxy, wall);
  // upper and lower sides
  LineInt(wall + middle + pathwidth, middle, width, middle, wall);
  LineInt(0, height - middle, width - wall - middle - pathwidth, height - middle, wall);

  int wally = wall + pathwidth + middle;
  LineInt(0, wally, width - wall - pathwidth, wally, wall);

  wally = 2 * wall + 2 * pathwidth + middle;
  LineInt(wall + pathwidth, wally, width, wally, wall);
}

//////////////////////////  Maze4  ////////////////////////

Maze4::Maze4() : Simulation(2440, 1220)
{
  const int maxx = width - 1;
  const int maxy = height - 1;
  const int wall = 35;
  const int middle = wall / 2;

  const int numpaths = 3;
  const int pathwidth = (width - wall * (numpaths + 1)) / numpaths;

  const double initialx = wall + pathwidth / 2;  // middle of the road

  // left and right outer sides near entrance and exit
  LineInt(middle, 0, middle, maxy, wall);
  LineInt(maxx - middle, 0, maxx - middle, maxy, wall);
  // upper and lower sides
  LineInt(wall + middle + pathwidth, middle, width, middle, wall);
  LineInt(0, height - middle, width - wall - middle - pathwidth, height - middle, wall);

  int wallx = wall + pathwidth + middle;
  LineInt(wallx, 0, wallx, height - wall - pathwidth, wall);

  wallx = 2 * wall + 2 * pathwidth + middle;
  LineInt(wallx, wall + pathwidth, wallx, height, wall);
}

//////////////////////////  Mars Maze 2019  /////////////////////////

MarsMaze::MarsMaze() : Simulation(3400, 1830)
{
  const int maxx = width - 1;
  const int maxy = height - 1;
  const int wall = 35;
  const int middle = wall / 2;
  const int xpath = 600;
  const int ypath = 550;

  // left and right outer sides
  LineInt(middle, 0, middle, maxy, wall);
  LineInt(maxx - middle, 0, maxx - middle, maxy, wall);
  // upper and lower sides
  LineInt(0, height - middle, maxx, height - middle, wall);
  LineInt(0, middle, maxx - 2 * wall - 2 * xpath, middle, wall);
  // left wall at start
  int wx = maxx - xpath - wall - middle;
  LineInt(wx, 0, wx, maxy - wall - ypath, wall);
  // left wall around first corner
  int wy = maxy - wall - ypath - middle;
  LineInt(maxx - 2 * wall - xpath, wy, maxx - 2 * wall - 2 * xpath, wy, wall);

  wy += middle;
  wx = maxx - 2 * wall - 2 * xpath - middle;
  LineInt(wx, wy, wx, wy - ypath - 2 * wall, wall);

  wx += middle;
  wy = maxy - 2 * wall - 2 * ypath - middle;
  LineInt(wx, wy, wx - 2 * xpath - 3 * wall, wy, wall);

  wy -= middle;
  wx = maxx - 4 * wall - middle - 4 * xpath;
  LineInt(wx, wy, wx, wy + ypath + wall, wall);

  wx = maxx - 3 * xpath - 3 * wall - middle;
  LineInt(wx, maxy, wx, maxy - wall - ypath, wall);
}