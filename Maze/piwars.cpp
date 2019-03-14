#include "Maze.h"
#include "Robot.h"
#include <iostream>
#include <string>
#include <exception>
#include <chrono>

int main(int argc, char* argv[])
{
  bool sim = false;
  int maxsteps = 100000;
  int test = 0;
  double maxSpeed = 0.0;
  double maxPerc = 100.0;

  for (int a = 1; a < argc; ++a) {
    if (strcmp(argv[a], "-help") == 0) {
      std::cout << "Options:" << std::endl;
      std::cout << "    -sim           : Run a marsmaze simulation instead of reality" << std::endl;
      std::cout << "    -steps <n>     : Number of processing steps to do, default 100000" << std::endl;
      std::cout << "    -maxspeed <f>  : Maximum speed of hardware, mm/s, default 0" << std::endl;
      std::cout << "    -maxperc <f>   : Maximum speed percentage, default 100.0" << std::endl;
      std::cout << "    -testrun <n>   : Run robot for specified time (ms), default 0 = no test" << std::endl;
      return 0;
    }
    else if (strcmp(argv[a], "-sim") == 0) {
      sim = true;
    }
    else if (strcmp(argv[a], "-steps") == 0) {
      if (++a < argc) maxsteps = std::stoi(argv[a]);
      else throw std::invalid_argument("No argument for -steps option");
    }
    else if (strcmp(argv[a], "-testrun") == 0) {
      if (++a < argc) test = std::stoi(argv[a]);
      else throw std::invalid_argument("No argument for -testrun option");
    }
    else if (strcmp(argv[a], "-maxspeed") == 0) {
      if (++a < argc) maxSpeed = std::stod(argv[a]);
      else throw std::invalid_argument("No argument for -maxspeed option");
    }
    else if (strcmp(argv[a], "-maxperc") == 0) {
      if (++a < argc) maxPerc = std::stod(argv[a]);
      else throw std::invalid_argument("No argument for -maxperc option");
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

  R.initiate(env.get());                        // Define dimensions and sensors (add maxspeed?)
  R.SetMaxSpeed(maxSpeed * maxPerc / 100.0);    // mm/s , speed limit
  env->setMaxSpeed(maxSpeed);                   // mm/s , maximum speed possible
  R.AdjustSpeed(Angle(0.0));

  try {
    int steps = 0;

    if (test != 0) {
      R.Move(env.get(), true);
      std::this_thread::sleep_for(std::chrono::milliseconds(test));
      R.Move(env.get(), false);
    }
    else {
      R.start(env.get());

      while (++steps <= maxsteps && !R.Stopped() && !env->finished()) {

        if (env->crashed()) {
          std::cout << "Crash" << std::endl;
          break;
        }
        std::cout << "Step " << steps << " - ";
        R.Correct(env.get());
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
