#!/bin/bash
#
# Start up Reliant
#
#!/bin/sh
tmux new-session -d -n robot '/home/pi/start'  

tmux new-window -d -n emacs 'emacs'  # -t 'robot'
#tmux split-window -v 'ipython'
#tmux split-window -h
tmux new-window -d  -n IMU '/home/pi/startIMU.sh'

#tmux -2 attach-session -d
