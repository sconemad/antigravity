Installation
============

# Startup script
Basic startup script is in ./bin/start-robot-tmux.sh
Ammend /etc/rc.local to run that:

> su - pi -c "/home/pi/bin/start-robot-tmux.sh"

# Helper scripts
Add in helper scripts that robot.py / display uses:

./bin/start-robot-tmux.sh - > ~/bin/
./bin/omni.sh -> ~/bin/

# Maze and IMU programs
./bin/startIMU.sh ->  /home/pi/startIMU.sh

and verify that the following binaries are compiled/installed/executable:

~/BerryIMU/gyro_accelerometer_tutorial03_kalman_filter/mh1_0mq
~/antigravity/Maze/Maze


Calibration
===========

The magnetometer used for the heading seems to require frequent calibration
Run the calibration tool, aligning each axis (+tive and -tive) with the local
field (in Cambridge:  approx north and 66 deg down) by maximising or minimising
the avg value, then Cntl-C and copy the resulting output to the calibration.h
header, and recompile the server & calibration tool



>  cd ~/BerryIMU/gyro_accelerometer_tutorial03_kalman_filter/
>  ./compass_calibration
>  emacs calibration.h
>  make arnold
>  make calibration
