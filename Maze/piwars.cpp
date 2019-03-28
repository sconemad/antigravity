#include "Maze.h"
#include "Robot.h"
#include <iostream>
#include <string>
#include <exception>
#include <chrono>

int main(int argc, char* argv[])
{
/*
  Pos p(0.0, 0.0, 0.0);
  double left = 20.0;   //  mm / sec
  double right = 10.0;
  double mean = (left + right) / 2.0;

  double totaldist = 150 * 2.0 * PI;   // Full circle
  double totaltime = totaldist / mean;

  for (int c = 0; c < 8; ++c) {
    p.Curve(left, right, 1000.0 * totaltime / 8.0, 100.0);
  }

  return 0;
*/
 
  bool sim = false;
  int maxsteps = 100000;
  double maxSpeed = 0.0;
  double maxPerc = 100.0;
  double left = 1.0;
  double right = 1.0;
  int offset = 60;
  int plandist = 100;
  double steep = 100.0;
  double angleFac = 0.25;
  bool correct = true;

  for (int a = 1; a < argc; ++a) {
    if (strcmp(argv[a], "-help") == 0) {
      std::cout << "Options:" << std::endl;
      std::cout << "    -sim            : Run a marsmaze simulation instead of reality" << std::endl;
      std::cout << "    -steps <n>      : Number of processing steps to do, default 100000" << std::endl;
      std::cout << "    -maxspeed <f>   : Maximum speed of hardware, mm/s, default 0" << std::endl;
      std::cout << "    -maxperc <f>    : Maximum speed percentage, default 100.0" << std::endl;
      std::cout << "    -offset <n>     : Offset for center of planning, default = 60mm" << std::endl;
      std::cout << "    -plandist <n>   : Distance for planning, default 100cm" << std::endl;
      std::cout << "    -steepness <n>  : steepness, default 100" << std::endl;
      std::cout << "    -anglefac <n>   : Angle change factor, default 0.25" << std::endl;
      std::cout << "    -GoStraight     : Just go in straight line, step = 50ms" << std::endl;
      std::cout << "    -Left <n>       : Start speed left, default 1.0" << std::endl;
      std::cout << "    -Right <n>      : Start speed right, default 1.0" << std::endl;
      return 0;
    }
    else if (strcmp(argv[a], "-sim") == 0) {
      sim = true;
    }
    else if (strcmp(argv[a], "-steps") == 0) {
      if (++a < argc) maxsteps = std::stoi(argv[a]);
      else throw std::invalid_argument("No argument for -steps option");
    }
    else if (strcmp(argv[a], "-maxspeed") == 0) {
      if (++a < argc) maxSpeed = std::stod(argv[a]);
      else throw std::invalid_argument("No argument for -maxspeed option");
    }
    else if (strcmp(argv[a], "-maxperc") == 0) {
      if (++a < argc) maxPerc = std::stod(argv[a]);
      else throw std::invalid_argument("No argument for -maxperc option");
    }
    else if (strcmp(argv[a], "-offset") == 0) {
      if (++a < argc) offset = std::stoi(argv[a]);
      else throw std::invalid_argument("No argument for -offset option");
    }
    else if (strcmp(argv[a], "-plandist") == 0) {
      if (++a < argc) plandist = std::stoi(argv[a]);
      else throw std::invalid_argument("No argument for -plandist option");
    }
    else if (strcmp(argv[a], "-steepness") == 0) {
      if (++a < argc) steep = std::stoi(argv[a]);
      else throw std::invalid_argument("No argument for -plandist option");
    }
    else if (strcmp(argv[a], "-anglefac") == 0) {
      if (++a < argc) angleFac = std::stod(argv[a]);
      else throw std::invalid_argument("No argument for -anglefac option");
    }
    else if (strcmp(argv[a], "-GoStraight") == 0) {
      correct = false;
    }
    else if (strcmp(argv[a], "-Left") == 0) {
      if (++a < argc) left = std::stod(argv[a]);
      else throw std::invalid_argument("No argument for -Left option");
    }
    else if (strcmp(argv[a], "-Right") == 0) {
      if (++a < argc) right = std::stod(argv[a]);
      else throw std::invalid_argument("No argument for -Right option");
    }
    else {
      std::cout << "Unknown option: " << argv[a] << std::endl;
    }
  }

#ifndef WIN32
  std::unique_ptr<Environment> env(sim ? (Environment*)new MarsMaze() : (Environment*)new Reality());
#else
  std::unique_ptr<Environment> env(new MarsMaze());
#endif

  Robot2 R(env.get());
  R.SetOffset(offset);
  R.SetSearchDistance(plandist);
  R.SetSteepness(steep);
  R.SetAngleFactor(angleFac);

  R.initiate(env.get());                        // Define dimensions and sensors (add maxspeed?)
  R.SetMaxSpeed(maxSpeed * maxPerc / 100.0);    // mm/s , speed limit
  env->setMaxSpeed(maxSpeed);                   // mm/s , maximum speed possible
  R.SetSpeed(left, right);
  env->setSpeed(left, right);

  try {
    int steps = 0;

    R.start(env.get());

    while (++steps <= maxsteps && !R.Stopped() && !env->finished()) {

      if (env->crashed()) {
        std::cout << "Crash" << std::endl;
        break;
      }
      std::cout << "Step " << steps << " - ";
      if (correct) {
        R.Correct(env.get());
      }
      else {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        std::cout << std::endl;
      }
    }
  }
  catch (std::exception& e) {
    std::cout << "Exception: " << e.what() << std::endl;
  }
  catch (...) {
    std::cout << "Unknown Exception" << std::endl;
  }

  env->setSpeed(0.0, 0.0);
  R.stop();

  env->write("maze.bmp", R.GetObstacles());
  return 0;
}
