#include "Robot.h"
#include "Maze.h"
#include <iostream>
#include <iterator>
#include <assert.h>
#include <random>
#include <chrono>

using Clock = std::chrono::high_resolution_clock;
using TimePoint = std::chrono::time_point<Clock>;

double safeminwalldist = std::numeric_limits<double>::max();
double minwalldist = std::numeric_limits<double>::max();


Robot::Robot(Environment* env) :
  robotposition(0.0, 0.0, env->getInitialAngle())
{
  const Obstacle ob(Point(0.0, 0.0));
  Point D(len / 2.0, wid / 2.0);
  safeminwalldist = ob.Value(D);
  double mdist = std::min(wid, len) / 2.0;
  minwalldist = ob.Value(Point(0.0, mdist));
}

void Robot::Move(Environment* env, double musec)
{
  // Move robot in internal representation
  Pos P = getRobotPos();
  {
    std::lock_guard<std::mutex> lg(speedMutex);
    P.Curve(speedl, speedr, musec / 1000.0, 240.0);

    setRobotPos(P);

    // Move in maze (sim or real)
    env->setSpeed(speedl, speedr);
  }

  // Leave drop obstacles
  Pos me = getRobotPos();
  me.Move(pi, 200.0);
  me.Move(hpi, wid / 2.0);

  if (me.Distance(lastDropRight) > 20) {
    lastDropRight = me;
    std::lock_guard<std::mutex> lg(obstacleMutex);
    drobstacles.push_back(Obstacle(me));
  }
  me.Move(-hpi, wid);
  if (me.Distance(lastDropLeft) > 20) {
    lastDropLeft = me;
    std::lock_guard<std::mutex> lg(obstacleMutex);
    drobstacles.push_back(Obstacle(me));
  }
}

void Robot::threadFunction(Environment* env)
{
  static TimePoint time = Clock::now();

  while (true) {
    for (auto& s : sensors) {
      if (cancelThread) return;

      TimePoint tm = Clock::now();
      auto d = tm - time;
      double musec = (double)std::chrono::duration_cast<std::chrono::microseconds>(d).count();
      time = tm;

      Move(env, musec);      // Move robot in internal representation
      env->MoveRobot(musec); // Move robot in simulation, if relevant

      const double distance = env->getDistance(s);  // Sleeps!!

      if (distance > 0.0) {
        if (distance < s.getMinDist()) {
          env->setSpeed(0.0, 0.0);
          cancelThread = true;
          std::cout << "Sensor minimum distance violated" << std::endl;
          return;
        }

        // Get location of sensor
        Pos p = getRobotPos();
        s.Process(p);
        // Get location of hit
        p.Move(s.getAngle(), distance);

        // Only add obstacle if it's not too far away
        // and not too close to the last one
        const double DistToLast = s.DistanceToLast(p);

        if (DistToLast > 15.0 && distance < 10000.0) {
          s.SetLast(p);
          std::lock_guard<std::mutex> lg(obstacleMutex);
          obstacles.push_back(Obstacle(p));
        }

        // Wait, to prevent next measurement to respond to last one's sound
        // We assume we need to wait for sound to travel at least 2 meters
        // but we can subtract the distance it has already travelled
        const double dist = 2000 - 2.0 * distance;
        if (dist > 0.0) {
          const unsigned int m = 1000 * toint(dist) / 343;
          std::this_thread::sleep_for(std::chrono::microseconds(m));
        }
      }
    }
  }
}


/////////////////////////// Node ///////////////////////////////////////////////

struct Node
{
  double maxheight = std::numeric_limits<double>::max();  // max height of path
  double height = std::numeric_limits<double>::max();
  double pathlen = std::numeric_limits<double>::max();
  bool visited = false;
  bool destination = false;
  short px = -1, py = -1; // previous node

  // Connecting via N is better than my existing connection
  bool bettervia(const Node& N) const {
    return maxheight > std::max(height, N.maxheight) ||
           (maxheight == N.maxheight && N.pathlen + height < pathlen);
  }

  void Connect(const Node& N, int x, int y) {
    maxheight = std::max(height, N.maxheight);
    pathlen = N.pathlen + height;
    px = x;
    py = y;
  }

  bool BetterDistination(const Node& N) const {
    return maxheight < N.maxheight ||
           (maxheight == N.maxheight && height < N.height);
  }
};

void Robot::Correct(Environment* env)
{
  {
    std::lock_guard<std::mutex> lg(obstacleMutex);

    const unsigned int MaxObstacles = 500;
    const unsigned int MaxDrobstacles = 10;

    if (obstacles.size() > MaxObstacles) {
      const int to_remove = obstacles.size() - MaxObstacles;
      obstacles.erase(obstacles.begin(), obstacles.begin() + to_remove);
    }
    if (drobstacles.size() > MaxDrobstacles) {
      const int to_remove = drobstacles.size() - MaxDrobstacles;
      drobstacles.erase(drobstacles.begin(), drobstacles.begin() + to_remove);
    }
  }

  const unsigned int vecsize = searchdist * 2 + 1;
  Vector2D<Node> space(vecsize, vecsize);

  const Point start(searchdist, searchdist);

  std::vector< std::pair< unsigned int, unsigned int > > notvisited;
  notvisited.reserve(50);
  notvisited.push_back({ searchdist, searchdist });
  int totalnodes = 0;

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
  std::cout << "Position: " << RPos.x() << ", " << RPos.y();
  std::cout << " Angle: " << RPos.getAngle();

  Pos centre = RPos;
  centre.Move(offset);
  const Point origin(centre.x() - searchdist * 10.0, centre.y() - searchdist * 10.0);

  // Prepare start node
  Node& startNode = space.Get(searchdist, searchdist);
  startNode.height = getHeight(origin + Point(searchdist * 10.0, searchdist * 10.0));
  startNode.maxheight = startNode.height;
  startNode.pathlen = startNode.height; // length is sum of heights, for now

  Node BestDestinationNode;
  int nodes = 0;

  while (true) {
    ++nodes;

    // Find the 'current' Node, the one with the best maximum height
    double bestscore = std::min(minwalldist, BestDestinationNode.maxheight);
    unsigned int bestindex = notvisited.size();

    for (unsigned int nv = 0; nv < notvisited.size(); ++nv) {
      const auto& p = notvisited[nv];
      const Node& n = space.Get(p.first, p.second);

      if (n.maxheight < bestscore)
      {
        bestscore = n.maxheight;
        bestindex = nv;
      }
    }

    if (bestindex == notvisited.size()) break;

    const int bestx = notvisited.at(bestindex).first;
    const int besty = notvisited.at(bestindex).second;
    notvisited.erase(notvisited.begin() + bestindex);

    Node& currentNode = space.Get(bestx, besty);
    // Mark as visited
    currentNode.visited = true;

    // Process neighbours

    const int xstart = (bestx > 0) ? bestx - 1 : bestx;
    const int xend = (bestx + 1 < (int)vecsize) ? bestx + 1 : bestx;

    for (int x = xstart; x <= xend; ++x) 
    {
      const int ystart = (besty > 0) ? besty - 1 : besty;
      const int yend = (besty + 1 < (int)vecsize) ? besty + 1 : besty;

      for (int y = ystart; y <= yend; ++y)
      {
        Node& Neighbour = space.Get(x, y);
        //if (Neighbour.visited) continue;  // Correct according to Dijkstra

        if (Neighbour.height == std::numeric_limits<double>::max())
        {
          Neighbour.height = getHeight(origin + Point(10.0 * x, 10.0 * y));
          Neighbour.Connect(currentNode, bestx, besty);
          if (!Neighbour.destination) notvisited.push_back({x, y});
        }
        else if (Neighbour.bettervia(currentNode))
        {
          Neighbour.Connect(currentNode, bestx, besty);
        }

        if (Neighbour.destination && Neighbour.BetterDistination(BestDestinationNode)) {
          BestDestinationNode = Neighbour;
        }
      }
    }
  }

  std::cout << totalnodes << " nodes, " << nodes << " visited";

  // Trace path back to robot
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

  // Everything should be relative to robot!

  for (int i = 1; i <= numsteps; ++i) {
    const Point P = plotpath.at(plotpath.size() - i);
    Angle tmp = AngleFromPos(P.x() - searchdist, P.y() - searchdist);
    tmp -= RPos.getAngle();
    sumangle += tmp;
  }

  const double meanangle = sumangle / numsteps;
  std::cout << ", Mean angle = " << meanangle;
  AdjustSpeed(meanangle);
  env->setSpeed(speedl, speedr);

  std::cout << std::endl;
}

const std::vector<Point> Robot::GetObstacles() const
{
  std::vector<Point> vec;
  std::lock_guard<std::mutex> lg(obstacleMutex);

  vec.reserve(obstacles.size() + drobstacles.size() + plotpath.size());

  for (const Obstacle& ob : obstacles) {
    vec.emplace_back(ob);
  }
  for (const Obstacle& ob : drobstacles) {
    vec.emplace_back(ob);
  }

  Pos C = getRobotPos();
  C -= Point(searchdist * 10, searchdist * 10);

  for (const Point& p : plotpath) {
    Point rp = p;
    rp *= 10.0;
    rp += C;
    rp.Move(C.getAngle(), offset);
    vec.emplace_back(rp);
  }

  return vec;
}

void Robot1::initiate(Environment* env)
{
  len = 260;
  wid = 240;
  env->setRobotDimensions(static_cast<int>(len), static_cast<int>(wid));

  sensors.push_back(Sensor(1, -wid / 2.0, len / 2.0, Angle(-hpi), 20.0));
  sensors.push_back(Sensor(2, -wid / 4.0, len / 2.0, Angle(qpi)));
  sensors.push_back(Sensor(3, 0.0, len / 2.0, Angle(0)));
  sensors.push_back(Sensor(4, wid / 4.0, len / 2.0, Angle(-qpi)));
  sensors.push_back(Sensor(5, wid / 2.0, len / 2.0, Angle(hpi), 20.0));
}

void Robot2::initiate(Environment* env)
{
  len = 110;
  wid = 245;
  env->setRobotDimensions(static_cast<int>(len), static_cast<int>(wid));

  sensors.push_back(Sensor(1, -wid / 4.0, len / 2.0 + 33.0, Angle(-pi / 3.0), 40.0));
  sensors.push_back(Sensor(2, 0.0, len / 2.0 + 55.0, Angle(0.0), 30.0));
  sensors.push_back(Sensor(3, wid / 4.0, len / 2.0 + 33.0, Angle(pi / 3.0), 40.0));
}

void Robot3::initiate(Environment* env)
{
  len = 110;
  wid = 245;
  env->setRobotDimensions(static_cast<int>(len), static_cast<int>(wid));

  sensors.push_back(Sensor(1, -wid / 4.0, len / 2.0 + 33.0, Angle(-pi / 4.0), 40.0));
  sensors.push_back(Sensor(2, 0.0, len / 2.0 + 55.0, Angle(0.0), 30.0));
  sensors.push_back(Sensor(3, wid / 4.0, len / 2.0 + 33.0, Angle(pi / 4.0), 40.0));
}
