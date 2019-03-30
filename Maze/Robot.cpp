#include "Robot.h"
#include "Maze.h"
#include <iostream>
#include <iterator>
#include <assert.h>
#include <random>
#include <chrono>

using Clock = std::chrono::high_resolution_clock;
using TimePoint = std::chrono::time_point<Clock>;

static double safeminwalldist = std::numeric_limits<double>::max();
static double minwalldist = std::numeric_limits<double>::max();

static constexpr unsigned int MaxObstacles = 50;
static constexpr unsigned int MaxDrobstacles = 20;

static constexpr double MaxObstDistance = 1100.0;

double Robot::Obstacle::steepness = 100.0;

Robot::Robot(Environment* env) :
  robotposition(0.0, 0.0, env->getInitialAngle())
{
  const Obstacle ob(Point(0.0, 0.0));
  Point D(len / 2.0, wid / 2.0);
  safeminwalldist = ob.Value(D);
  const double mdist = std::min(wid, len) / 2.0;
  minwalldist = ob.Value(Point(0.0, mdist));
  obstacles.reserve(MaxObstacles + 10);
  drobstacles.reserve(MaxDrobstacles + 2);
}

void Robot::Move(Environment* env, double musec)
{
  // Move robot in internal representation
  Pos P = getRobotPos();
  {
    std::lock_guard<std::mutex> lg(speedMutex);
    P.Curve(speedl, speedr, musec / 1000.0, turnWidth());
    setRobotPos(P);
  }

  // Leave drop obstacles
  Pos me = P;
  me.Move(pi, 200.0);
  
  me.Move(hpi, wid / 2.0);
  if (me.Distance(lastDropRight) > 20) {
    lastDropRight = me;
    std::lock_guard<std::mutex> lg(drobstacleMutex);
    drobstacles.push_back(Obstacle(me));
  }

  me.Move(-hpi, wid);
  if (me.Distance(lastDropLeft) > 20) {
    lastDropLeft = me;
    std::lock_guard<std::mutex> lg(drobstacleMutex);
    drobstacles.push_back(Obstacle(me));
  }
}

void Robot::threadFunction(Environment* env)
{
  static TimePoint time = Clock::now();

  while (true) {
    for (Sensor& s : sensors)
    {
      if (cancelThread) return;

      const TimePoint tm = Clock::now();
      const auto d = tm - time;
      const double musec = (double)std::chrono::duration_cast<std::chrono::microseconds>(d).count();
      if (musec < 20000) {
        // We don't want to do more than 50 measurements a second
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        continue; // do not increment snum
      }
      time = tm;

      env->MoveRobot(musec); // Move robot in simulation, if relevant

      const double distance = env->getDistance(s);  // Sleeps in sim!!

      Move(env, musec);      // Move robot in internal representation

      if (distance > 0.0) {
        if (distance < s.getMinDist()) {
          env->setSpeed(0.0, 0.0);
          cancelThread = true;
          std::cout << "Sensor minimum distance violated" << std::endl;
          return;
        }

        if (distance > MaxObstDistance) {
          continue;
        }

        // Get location of sensor
        Pos p = getRobotPos();

        // Now process
        s.Process(p);
        // Get location of hit
        p.Move(s.getAngle(), distance);

        std::lock_guard<std::mutex> lg(obstacleMutex);
        obstacles.push_back(Obstacle(p));

/*      if (!s.Last()) {
          // First call for this sensor, make sure to add obstacle
          // Could skip this. First measurement will then be verified
          // The choice is between safer and faster
          s.SetLast(p);
          verify = false;
          std::lock_guard<std::mutex> lg(obstacleMutex);
          obstacles.push_back(Obstacle(p));
          ++snum;
          continue;
        }

        // Only add obstacle if it's not too close to the last one, or too far
        const double lastdist = s.DistanceToLast(p);

        if (lastdist < 15 && !verify) {
          // Too close and not verifying, do nothing
          ++snum;
          continue;
        }

        s.SetLast(p);   // Either to add or verify

        if (lastdist < 50) {
          verify = false;
          std::lock_guard<std::mutex> lg(obstacleMutex);
          obstacles.push_back(Obstacle(p));
        }
        else {
          // Too far, redo sensor to verify if measurement is correct
          verify = true;
          continue;
        } */
      }
    }
  }
}


/////////////////////////// Node ///////////////////////////////////////////////

struct Node
{
  float maxheight = std::numeric_limits<float>::max();  // max height of path to this node
  float height = std::numeric_limits<float>::max();     // height at this node
  float pathlen = std::numeric_limits<float>::max();
  short px = -1, py = -1; // previous node
  bool destination = false;

  bool CheckBestIn(short mx, short my, const Vector2D<Node>& nvec) {
    assert(heightCalculated());
    bool change = false;
    for (short x = mx - 1; x <= mx + 1; ++x) {
      if (x >= 0 && x < (short)nvec.xsize()) {
        for (short y = my - 1; y <= my + 1; ++y) {
          if (y >= 0 && y < (short)nvec.ysize() && (x != mx || y != my)) {
            const Node& other = nvec.Get(x, y);
            if (bettervia(other)) {
              Connect(other, x, y);
              change = true;
            }
          }
        }
      }
    }
    return change;
  }

  bool heightCalculated() const {
    return height < std::numeric_limits<float>::max();
  }

  // Connecting via N is better than my existing connection
  bool bettervia(const Node& N) const {
    const float Nmax = std::max(height, N.maxheight);
    return maxheight > Nmax || (maxheight == Nmax && N.pathlen + height < pathlen);
  }

  void Connect(const Node& N, int x, int y) {
    maxheight = std::max(height, N.maxheight);
    pathlen = N.pathlen + height;
    px = x;
    py = y;
  }

  bool BetterDistination(const Node& N) const {
    return maxheight < N.maxheight || (maxheight == N.maxheight && pathlen < N.pathlen);
  }
};

void Robot::Correct(Environment* env)
{
  {
    std::lock_guard<std::mutex> lg(obstacleMutex);

    if (obstacles.size() > MaxObstacles) {
      const int to_remove = obstacles.size() - MaxObstacles;
      obstacles.erase(obstacles.begin(), obstacles.begin() + to_remove);
    }
  }
  {
    std::lock_guard<std::mutex> lg(drobstacleMutex);

    if (drobstacles.size() > MaxDrobstacles) {
      const int to_remove = drobstacles.size() - MaxDrobstacles;
      drobstacles.erase(drobstacles.begin(), drobstacles.begin() + to_remove);
    }
  }

  const unsigned int vecsize = searchdist * 2 + 1;
  static Vector2D<Node> space(vecsize, vecsize);
  space.clear();
  space.resize(vecsize, vecsize);

  const Point start(searchdist, searchdist);

  std::vector< std::pair< unsigned short, unsigned short > > notvisited;
  notvisited.reserve(50);
  notvisited.push_back({ searchdist, searchdist });
  unsigned int totalnodes = 0;

  for (unsigned int x = 0 ; x < vecsize; ++x) {
    for (unsigned int y = 0; y < vecsize; ++y) {
      if (start.Distance(Point(x, y)) + 0.1 >= searchdist)
      {
        // Set all Nodes beyond range as destinations.
        space.Get(x, y).destination = true;
      }
      else {
        ++totalnodes;
      }
    }
  }

  const Pos RPos = getRobotPos();

  Pos centre = RPos;
  centre.Move(offset);
  const Point origin(centre.x() - searchdist * 10.0, centre.y() - searchdist * 10.0);

  // Prepare start node
  Node& startNode = space.Get(searchdist, searchdist);
  startNode.height = (float)getHeight(origin + Point(searchdist * 10.0, searchdist * 10.0));
  startNode.maxheight = startNode.height;
  startNode.pathlen = startNode.height; // length is sum of heights, for now

  Node BestDestinationNode;
  int nodes = 0;

  while (true) {
    ++nodes;

    // Find the 'current' Node, the one with the best maximum height
    float bestscore = std::min((float)minwalldist, BestDestinationNode.maxheight);
    unsigned int bestindex = notvisited.size();

    for (std::size_t nv = 0; nv < notvisited.size(); ++nv) {
      const auto& p = notvisited[nv];
      const float mh = space.Get(p.first, p.second).maxheight;

      if (mh < bestscore)
      {
        bestscore = mh;
        bestindex = nv;
      }
    }

    if (bestindex == notvisited.size()) break;

    const int bestx = notvisited.at(bestindex).first;
    const int besty = notvisited.at(bestindex).second;
    notvisited.erase(notvisited.begin() + bestindex);

    Node& currentNode = space.Get(bestx, besty);

    // Process neighbours

    const int xstart = (bestx > 0) ? bestx - 1 : bestx;
    const int xend = (bestx + 1 < (int)space.xsize()) ? bestx + 1 : bestx;
    const int ystart = (besty > 0) ? besty - 1 : besty;
    const int yend = (besty + 1 < (int)space.ysize()) ? besty + 1 : besty;

    // First initiate all neighbours that are still uninitiated
    for (int x = xstart; x <= xend; ++x) 
    {
      for (int y = ystart; y <= yend; ++y)
      {
        Node& Neighbour = space.Get(x, y); // Could be me, doesn't matter

        if (!Neighbour.heightCalculated())
        {
          // Initiate neighbour, connect to best, could be me
          Neighbour.height = (float)getHeight(origin + Point(10.0 * x, 10.0 * y));
          Neighbour.CheckBestIn(x, y, space);
          if (!Neighbour.destination && Neighbour.height <= minwalldist) {
            notvisited.push_back({x, y});
          }
        }
      }
    }

    // All are now initialised and everybody is connected to someone
    // We just need to see if we can connect things up a bit better

    bool changed = true;

    while (changed)
    {
      changed = false;

      for (int x = xstart; x <= xend; ++x) 
      {
        for (int y = ystart; y <= yend; ++y)
        {
          Node& N = space.Get(x, y);
          
          if (N.CheckBestIn(x, y, space)) {
            changed = true;
          }

          if (N.destination && N.BetterDistination(BestDestinationNode)) {
            BestDestinationNode = N;
          }
        }
      }
    }
  }

  std::cout << totalnodes << " nodes, " << nodes << " visited";

  // Trace path back to robot, for visualisation
  plotpath.clear();

  short px = BestDestinationNode.px;
  short py = BestDestinationNode.py;

  while (px != -1 && py != -1) {
    plotpath.push_back(Point(px, py));
    const Node& next = space.Get(px, py);
    px = next.px;
    py = next.py;
  }

  // Find direction to go in, based on first steps on path
  const int numsteps = 20;
  double sumangle = 0.0; // do not use Angle class here!

  // Everything should always be relative to robot!

  for (int i = 1; i <= numsteps; ++i) {
    const Point P = plotpath.at(plotpath.size() - i);
    Angle a = AngleFromPos(P.x() - searchdist, P.y() - searchdist);
    a -= RPos.getAngle();
    sumangle += a;
  }

  Angle meanangle(sumangle / numsteps);

  // std::cout << ", Mean angle = " << meanangle;
  AdjustSpeed(meanangle);
  env->setSpeed(speedl, speedr);

  std::cout << std::endl;
}

const std::vector<Point> Robot::GetObstacles() const
{
  std::vector<Point> vec;
  std::lock_guard<std::mutex> lg(obstacleMutex);
  std::lock_guard<std::mutex> ld(drobstacleMutex);

  vec.reserve(obstacles.size() + drobstacles.size() + plotpath.size() + 1);

  for (const Obstacle& ob : obstacles) {
    vec.emplace_back(ob);
  }
  for (const Obstacle& ob : drobstacles) {
    vec.emplace_back(ob);
  }

  Pos C = getRobotPos();
  vec.emplace_back(C);
  C.Move(offset);
  C -= Point(searchdist * 10, searchdist * 10);

  for (Point rp : plotpath) {
    rp *= 10.0;
    rp += C;
    vec.emplace_back(rp);
  }

  return vec;
}

void Robot1::initiate(Environment* env)
{
  len = 260;
  wid = 240;
  tire = 10;
  env->setRobotDimensions(static_cast<int>(len), static_cast<int>(wid), static_cast<int>(tire));

  sensors.push_back(Sensor(1, -wid / 2.0, len / 2.0, Angle(-hpi), 20.0));
  sensors.push_back(Sensor(2, -wid / 4.0, len / 2.0, Angle(qpi)));
  sensors.push_back(Sensor(3, 0.0, len / 2.0, Angle(0)));
  sensors.push_back(Sensor(4, wid / 4.0, len / 2.0, Angle(-qpi)));
  sensors.push_back(Sensor(5, wid / 2.0, len / 2.0, Angle(hpi), 20.0));
}

void Robot2::initiate(Environment* env)
{
  len = 120.0;
  wid = 190.0;
  tire = 25.0;

  env->setRobotDimensions(static_cast<int>(len), static_cast<int>(wid), static_cast<int>(tire));

  sensors.push_back(Sensor(1, -30.0, 45.0, Angle(pi / 3.0),  120.0));
  sensors.push_back(Sensor(2,   0.0, 35.0, Angle(0.0),       150.0));
  sensors.push_back(Sensor(3,  30.0, 45.0, Angle(-pi / 3.0), 120.0));
}

void Robot3::initiate(Environment* env)
{
  len = 110;
  wid = 245;
  tire = 10;
  env->setRobotDimensions(static_cast<int>(len), static_cast<int>(wid), static_cast<int>(tire));

  sensors.push_back(Sensor(1, -wid / 4.0, len / 2.0 + 33.0, Angle(-pi / 4.0), 60.0));
  sensors.push_back(Sensor(2, 0.0, len / 2.0 + 55.0, Angle(0.0), 50.0));
  sensors.push_back(Sensor(3, wid / 4.0, len / 2.0 + 33.0, Angle(pi / 4.0), 60.0));
}
