#ifndef _PI_WARS_ROBOT_H_
#define _PI_WARS_ROBOT_H_

#include "Utils.h"
#include <vector>
#include <algorithm>
#include <thread>
#include <atomic>
#include <mutex>

class Environment;

class Robot
{
protected:
  class Obstacle : public Point
  {
  public:
    static double steepness;

    explicit Obstacle(const Point& p) : Point(p) {}

    static double height(double distance) {
      return pow(2.0, -(distance - 100) / steepness);
    }

    double Value(const Point& p) const {
      return height(Distance(p));
    }
  };

  mutable std::mutex obstacleMutex;
  mutable std::mutex drobstacleMutex;
  std::vector< Obstacle > obstacles;    // Created by distance measurements
  std::vector< Obstacle > drobstacles;  // Created by dropping an obstacles behind the robot

  double getHeight(const Point p) const
  {
    // Get distance to nearest obstacle
    double nearestssq = std::numeric_limits<double>::max();
    {
      std::lock_guard<std::mutex> lg(obstacleMutex);
      for (const Obstacle& ob : obstacles) {
        nearestssq = std::min(nearestssq, ob.SumOfSquares(p));
      }
    }
    {
      std::lock_guard<std::mutex> lg(drobstacleMutex);
      for (const Obstacle& ob : drobstacles) {
        nearestssq = std::min(nearestssq, ob.SumOfSquares(p));
      }
    }
    return Obstacle::height(sqrt(nearestssq));
  }

  // Dimensions
  double wid = 0.0;
  double len = 0.0;
  double tire = 0.0;

  mutable std::mutex locationMutex;
  Pos robotposition;

  mutable std::mutex speedMutex;
  double maxspeed = 0.0;
  double speedl = 0.0;  // mm/sec
  double speedr = 0.0;
  double angleFactor = 0.25;

  int searchdist = 100; // radius, cm (40 works)
  int offset = 60;      // centre location, mm (40 works)

  std::vector< Point > plotpath;

  std::vector< Sensor > sensors;

  std::thread workerThread;
  std::atomic_bool cancelThread {false};

  Point lastDropLeft;
  Point lastDropRight;

public:
  explicit Robot(Environment* env);
  virtual ~Robot() { stop(); }

  double turnWidth() const {
    return wid - tire;
  }

  void start(Environment* env) {
    std::thread t([this, env] { threadFunction(env); });
    t.swap(workerThread);
  }

  void stop() {
    cancelThread = true;
    if (workerThread.joinable()) workerThread.join();
  }

  bool Stopped() const { return cancelThread; }

  virtual void initiate(Environment* env) = 0;
  void threadFunction(Environment* env);

  void SetMaxSpeed(double m) {
    maxspeed = m;
  }

  void SetSpeedFraction(double left, double right) {
    speedl = left * maxspeed;
    speedr = right * maxspeed;
  }

  void SetOffset(int mm) {
    offset = mm;
  }

  void SetSearchDistance(int cm) {
    searchdist = cm;
  }

  void SetSteepness(double s) {
    Obstacle::steepness = s;
  }

  void SetAngleFactor(double f) {
    angleFactor = f;
  }

  // Input is double, as this could be more than +/- pi, but will
  // be divided for the direction change
  void AdjustSpeed(double a) {

    Angle diff(a * angleFactor);

    std::lock_guard<std::mutex> lg(speedMutex);
    Angle2Speed(diff, maxspeed, 50, turnWidth(), speedl, speedr);
  }

  void Move(Environment* M, double musec);

  void Correct(Environment* env);

  const std::vector<Point> GetObstacles() const;

  Pos getRobotPos() const {
    std::lock_guard<std::mutex> lg(locationMutex);
    return robotposition;
  }
  void setRobotPos(Pos p) {
    std::lock_guard<std::mutex> lg(locationMutex);
    robotposition = p;
  }
};

// Robot 1 is essentially the 2018 piwars robot, but without the 'gun'
class Robot1 : public Robot {
public:
  explicit Robot1(Environment* env) : Robot(env) {}
  void initiate(Environment* env) override;
};

// Robot2 is a test robot, with two driven wheels and 3 sensors, 60 degrees
class Robot2 : public Robot {
public:
  explicit Robot2(Environment* env) : Robot(env) {}
  void initiate(Environment* env) override;
};

// Robot2 is a test robot, with two driven wheels and 3 sensors, 45 degrees
class Robot3 : public Robot {
public:
  explicit Robot3(Environment* env) : Robot(env) {}
  void initiate(Environment* env) override;
};

#endif
