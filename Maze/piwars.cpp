#include "Maze.h"
#include "Robot.h"
#include <iostream>

int main(int argc, char* argv[])
{
  //MarsMaze M;
  Maze2 M;
  //Reality M;
  Robot3 R(&M);

  R.initiate(&M);
  R.SetMaxSpeed(49);  // mm/s
  M.setMaxSpeed(49);
  R.AdjustSpeed(Angle(0.0));

  try {
    int steps = 0;

    R.start(&M);

    while (++steps <= 10 && !R.Stopped() && !M.finished()) {

      if (M.crashed()) {
        std::cout << "Crash" << std::endl;
        break;
      }
      std::cout << "Step " << steps << " - ";
      R.Correct(&M);
    }
  } catch (std::exception& e) {
    std::cout << "Exception: " << e.what() << std::endl;
  } catch (...) {
    std::cout << "Unknown Exception" << std::endl;
  }

  M.setSpeed(0.0, 0.0);
  R.stop();

  M.write("maze.bmp", R.GetObstacles());
  return 0;
}
