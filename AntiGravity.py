# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# AntiGravity - core Bot class for AntiGravity
#

import os
import struct
import array
import asyncio
import math
import time
import picamera

from Bot import Bot
from Drive import Drive
from DriveMD25 import DriveMD25
from DrivePiconZero import DrivePiconZero
from Echo import Echo
from CtrlServer import CtrlServer
from JS import JS, JSCallback
from Camera import Camera
from Rainbow import Rainbow
from Dummy import Dummy
from Distance import Distance
from Testline import Testline
from Calibrate import Calibrate
from Turtle import Turtle
#from Maze import Maze
#from Maze_deadreckoning import Maze2
from Straightline import Straightline

class AntiGravity(Bot, JSCallback):

    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.modulemode = "straightline" # Currently active module, see below
        # TTD should really validate it's in self.modules
        self.currentmode = "Manual / " + self.modulemode

        # Create the appropriate Drive class for this robot
        self.drive = 0
        try: self.drive = DriveMD25(self)
        except: pass
        if self.drive == 0:
            try: self.drive = DrivePiconZero(self)
            except: pass
        if self.drive == 0: self.drive == Drive(self)
        self.logMsg("Drive: %s" % (type(self.drive).__name__))

        self.echo = Echo(self)
        self.ctrlServer = CtrlServer(self)
        self.turtle = Turtle(self)
        self.js = JS(self)
        self.camera = Camera()
        
        # Mode modules - launched by the 'x' (AKA SQUARE) button
        # Functions MUST implement a start() method
        self.modules = {
            "rainbow": Rainbow(self),
            "distance": Distance(self),
            "testline": Testline(self),
            "straightline": Straightline(self),
            "calibrate": Calibrate(self),
#            "maze": Maze(self),
#            "maze2": Maze2(self),
            "dummy": Dummy(self)
        }
        self.modulesList = self.modules.items()
        # Used by Turtle, Calibrate etc - global store so calibrate can update
        self.turnCorrectionFactor=0.915
        self.distCorrectionFactor=1

    def __del__(self):
        self.logfile.close()
        
    def next_module(self,auto=None):
        if auto is not None:
            self.logMsg("Finished Auto Module:" + self.modulemode)
        try:
            nm = self.modulesList.next()
        except StopIteration:
            self.logMsg("Orobous: Restarting module list")
            self.modulesList = self.modules.items()
            nm = self.modulesList.next()
            pass
        # Boilerplate
        self.modulemode = nm[0]
        self.currentmode = "Manual / " + self.modulemode
        return nm[0]
         
    def get_camera(self):
        return self.camera

    def pause(self,timeSec):
        "Pause, with logging"
        self.logMsg(" --- Pausing for %d seconds ---" % int(timeSec))
        time.sleep(timeSec)
        
    def setTimer(self, t, cb):
        self.loop.call_later(t, cb, [])

    def leftStick(self, x, y):
        "Notification of a gamepad left analog stick event"
        self.logMsg('LEFT_STICK: %.3f %.3f' % (x, y))

    def rightStick(self, x, y):
        "Notification of a gamepad right analog stick event"
        self.logMsg('RIGHT_STICK: %.3f %.3f' % (x, y))
        self.drive.setDriveXY(x, y)
    
    def dpadEvent(self, x, y):
        "Notification of a gamepad directional pad event"
        self.logMsg('DPAD: %.3f %.3f' % (x, y))
        self.drive.setDriveXY(x, y)

    def buttonEvent(self, b, down):
        "Notification of a gamepad button event"
        if (down):
            self.logMsg("BUTTON %s down" % (b))
        else:
            self.logMsg("BUTTON %s up" % (b))
        if (down): return
        if (b == 'tl'): self.drive.setFlip(0)
        if (b == 'tl2'): self.drive.setFlip(1)
        if (b == 'tr'): self.drive.decSpeedFactor()
        if (b == 'tr2'): self.drive.incSpeedFactor()
        if (b == 'thumbl'):
             print("nothing")
        if (b == 'x'):  # AKA square
            self.currentmode = "Auto : " + self.modulemode
            module = self.modules.get(self.modulemode,None)
            self.logMsg("Starting Auto Module:" + self.modulemode)
            module.start()
            self.logMsg("(Auto module started; control returned to main)")
        if (b == "y"): # AKA triangle
            self.logMsg("Selecting next module:" + self.next_module())
        if (b == 'select'):
            self.loop.stop()
