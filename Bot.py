# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# Bot - Bot base class
#

import os
import datetime

class Bot:
    
    def __init__(self):
        self.logfile = open('/home/pi/vncbot.log', 'w')

    def __del__(self):
        self.logfile.close()
        
    def logMsg(self, msg):
        s = "%s %s" % (datetime.datetime.now(), msg)
        print(s)
        self.logfile.write(s)
        self.logfile.write("\n")
