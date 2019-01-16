#ifndef _PI_WARS_MAZE_H_
#define _PI_WARS_MAZE_H_

#include "Utils.h"
#include "Comms.h"
#include <vector>
#include <iostream>
#include <mutex>


class Environment
{
protected:
  int robotLen = 0;
  int robotWidth = 0;

  mutable std::mutex posMutex;
  Pos RobotPos;

public:
  Environment() : RobotPos(0.0, 0.0, 0.0) {}

  const Pos GetRobotPos() const {
    std::lock_guard<std::mutex> lg(posMutex);
    return RobotPos;
  }
  void SetRobotPos(const Pos& P) {
    std::lock_guard<std::mutex> lg(posMutex);
    RobotPos = P;
  }

  virtual void setRobotDimensions(int len, int wid) = 0;
  double getRobotWidth()  const { return robotWidth; }
  double getRobotLength() const { return robotLen; }
  virtual void setSpeed(double left, double right) = 0;

  Angle getInitialAngle() const { return Angle(0.0); }

  virtual void MoveRobot(double musec) {}
  
  // Get a distance measurement from a sensor
  virtual double getDistance(const Sensor& s) = 0;

  // Tells if the robot has hit a wall, in the sim.
  // I'm not sure if we can detect this in reality
  // The sensors all have safety distances, so this shouldn't happen.
  virtual bool crashed() { return false; }

  // Tells if the robot has finished the course correctly,
  // not possible in reality.
  virtual bool finished() { return false; }

  // Write result of simulation to bmp file
  virtual void write(std::string filename, const std::vector<Point>& pvec) {}
};

struct Corners
{
  Point FL;
  Point FR;
  Point BL;
  Point BR;
};

class Simulation : public Environment
{
protected:
  int width;
  int height;

  Pos InitialPos;

  std::mutex speedMutex;
  double speedl;  // speed in mm / sec
  double speedr;

  std::vector< std::vector < bool > > area;
  std::vector< std::pair< int, int > > Marks;

  bool SetPixel(int x, int y, int w = 0, bool h = false, bool detect = false);

  void LineInt(int x1, int y1, int x2, int y2, int thick) {
    Line(x1, y1, x2, y2, thick);
  }
  bool LineHit(Point a, Point b) {
    return LineHit(a.x(), a.y(), b.x(), b.y());
  }
  bool LineHit(double x1, double y1, double x2, double y2) {
    return Line(toint(x1), toint(y1), toint(x2), toint(y2), 0, true);
  }
  bool Line(Point a, Point b, int thick = 0) {
    return Line(toint(a.x()), toint(a.y()), toint(b.x()), toint(b.y()), thick);
  }
  bool Line(int x1, int y1, int x2, int y2, int thick = 0, bool detect = false);
  
  // Corners of robot bounding box
  Corners GetCorners(Pos p) const;

public:
  Simulation(int w, int h);

  void setRobotDimensions(int len, int wid) override {
    robotLen = len;
    robotWidth = wid;
    const double initialx = 35 + 200;       // middle of the road
    const double initialy = getRobotLength() / 2 + 10; // 1cm from bottom
    SetRobotPos(Pos(initialx, initialy, 0.0));
    InitialPos = GetRobotPos();
  }

  // Move the robot through the sim, not needed in the real world
  void MoveRobot(double musec) override;

  void setSpeed(double left, double right) override;

  // get a distance measurement from the gun
  double getDistance(const Sensor& s) override;

  // Tells if the robot has hit a wall, in the sim.
  // I'm not sure if we can detect this in reality
  bool crashed() override;

  bool finished() override;

  // Write result of simulation to bmp file
  void write(std::string filename, const std::vector<Point>& pvec) override;
};

// 2018 Piwars maze
class Maze1 : public Simulation
{
public:
  Maze1();
};

// Maze with vertical zigzags
class Maze2 : public Simulation
{
public:
  Maze2();
};

// Maze with horizontal zigzags
class Maze3 : public Simulation
{
public:
  Maze3();
};

// Maze with open space
class Maze4 : public Simulation
{
public:
  Maze4();
};

class MarsMaze : public Simulation
{
public:
  MarsMaze();

  void setRobotDimensions(int len, int wid) override {
    robotLen = len;
    robotWidth = wid;
    const double initialx = width - 330;       // middle of the road
    const double initialy = getRobotLength() / 2 + 10; // 1cm from bottom
    SetRobotPos(Pos(initialx, initialy, 0.0));
    InitialPos = GetRobotPos();
  }
};

class Reality : public Environment
{
public:
  // speed from 0.0 - 1.0, max speed is about 1100 mm/sec
  // arguments are in mm/sec too
  void setSpeed(double left, double right) override
  { 
    comms.setSpeed(left, right);
  }

  void setRobotDimensions(int len, int wid) override
  {}

  double getDistance(const Sensor& s) override
  { 
    switch (s.Num()) {
      case 1: return comms.getDistance(Comms::ECHO_LEFT);
      case 2: return comms.getDistance(Comms::ECHO_CENTRE);
      case 3: return comms.getDistance(Comms::ECHO_RIGHT);
      default: return -1.0;
    }
  }

private:
  Comms comms;
};

#endif
