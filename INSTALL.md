Installation
============

# Startup script
Basic startup script is in ./bin/start-robot-tmux.sh
Ammend /etc/rc.local to run that:

> su - pi -c "/home/pi/bin/start-robot-tmux.sh"

# Helper scripts
Add in helper scripts that robot.py / display uses:

./bin/start-robot-tmux.sh - > ~/bin/

# Maze and IMU programs
./bin/startIMU.sh ->  /home/pi/startIMU.sh

and verify that the following binaries are compiled/installed/executable:

~/BerryIMU/gyro_accelerometer_tutorial03_kalman_filter/mh1_0mq
~/antigravity/Maze/Maze
