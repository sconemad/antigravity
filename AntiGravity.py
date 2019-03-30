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
from Lidar import Lidar
from Servo import Servo
from CtrlServer import CtrlServer
from JS import JS, JSCallback
from Camera import Camera

# Modules
from Dummy import Dummy
from Shutdown import Shutdown
from Rainbow import Rainbow
from Distance import Distance
from Testline import Testline
from Calibrate import Calibrate
from Turtle import Turtle
from Display import Display
from Network import Network
from Heading import Heading
#from Maze import Maze
#from Maze_deadreckoning import Maze2
from Straightline import Straightline

class AntiGravity(Bot, JSCallback):

    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.voltage = 0
        self.speedFactor = 3
        self.flip = False
        
        # Create the appropriate Drive class for this robot
        self.drive = 0
        try: self.drive = DriveMD25(self)
        except: pass
        if self.drive == 0:
            try: self.drive = DrivePiconZero(self)
            except: pass
        if self.drive == 0: self.drive == Drive(self)
        self.logMsg("Drive: %s" % (type(self.drive).__name__))

        self.dist = Lidar(self)
        self.servo = Servo(self)
        self.ctrlServer = CtrlServer(self)
        self.turtle = Turtle(self)
        self.js = JS(self)
        self.camera = Camera()
        
        # Mode modules - launched by the 'x' (AKA SQUARE) button
        # Functions MUST implement a start() method
        self.modules = [
            Dummy(self),
            self.dist, # Lidar is also a module
            Shutdown(self),
            Network(self),
            Heading(self),
            Rainbow(self)
        ]
#            "rainbow": Rainbow(self),
#            "distance": Distance(self),
#            "testline": Testline(self),
#            "straightline": Straightline(self),
#            "calibrate": Calibrate(self),
#            "maze": Maze(self),
#            "maze2": Maze2(self),

        self.module = 0
        self.display = Display(self)
        self.batTimer([])
        
    def __del__(self):
        self.logfile.close()
        
    def get_camera(self):
        return self.camera

    def quit(self):
        self.loop.stop()
    
    def pause(self,timeSec):
        "Pause, with logging"
        self.logMsg(" --- Pausing for %d seconds ---" % int(timeSec))
        time.sleep(timeSec)
        
    def setTimer(self, t, cb):
        self.loop.call_later(t, cb, [])

    def batTimer(self, args):
        self.voltage = self.drive.getBatteryVoltage()
        self.logMsg("Battery voltage: %0.1fv" % (self.voltage))
        self.setTimer(10, self.batTimer)

    def getBatteryVoltage(self):
        return self.voltage

    def getModule(self):
        return self.modules[self.module]

    def startModule(self):
        mod = self.getModule()
        self.logMsg("Starting module: %s" % (mod.name))
        mod.start()

    def stopModule(self):
        mod = self.getModule()
        self.logMsg("Stopping module: %s" % (mod.name))
        mod.stop()

    def nextModule(self):
        self.module = self.module + 1
        if self.module >= len(self.modules): self.module = 0
        self.logMsg("Selected module: %s" % (self.getModule().name)) 

    def prevModule(self):
        self.module = self.module - 1
        if self.module < 0: self.module = len(self.modules) - 1
        self.logMsg("Selected module: %s" % (self.getModule().name)) 
        
    def manualDrive(self, x, y):
        m = 0
        if self.speedFactor == 1: m = 0.1
        elif self.speedFactor == 2: m = 0.2
        elif self.speedFactor == 3: m = 0.3
        elif self.speedFactor == 4: m = 0.4
        elif self.speedFactor == 5: m = 0.5
        else: m = 1.0
        rx = x * m
        if self.flip: ry = -y * m
        else: ry = y * m
        self.drive.setDriveXY(rx, ry)
            
    def leftStick(self, x, y):
        "Notification of a gamepad left analog stick event"
        self.logMsg('LEFT_STICK: %.3f %.3f' % (x, y))
        self.servo.setAngle(0, (x+1)*90)

    def rightStick(self, x, y):
        "Notification of a gamepad right analog stick event"
        self.logMsg('RIGHT_STICK: %.3f %.3f' % (x, y))
        self.manualDrive(x, y)

    def dpadEvent(self, x, y):
        "Notification of a gamepad directional pad event"
        self.logMsg('DPAD: %.3f %.3f' % (x, y))
        self.manualDrive(x/2, y)

    def buttonEvent(self, b, down):
        "Notification of a gamepad button event"
        if (down):
            self.logMsg("BUTTON %s down" % (b))
        else:
            self.logMsg("BUTTON %s up" % (b))
        if (down): return
        if (b == 'tl'):
            self.flip = False
            self.display.showFlip(self.flip)
        if (b == 'tl2'):
            self.flip = True
            self.display.showFlip(self.flip)
        if (b == 'tr'):
            if (self.speedFactor < 6):
                self.speedFactor = self.speedFactor + 1
            self.display.showSpeedFactor(self.speedFactor)
        if (b == 'tr2'):
            if (self.speedFactor > 1):
                self.speedFactor = self.speedFactor - 1
            self.display.showSpeedFactor(self.speedFactor)

        if (b == 'thumbl'): print("nothing")
        if (b == 'thumbr'): self.drive.halt()
        if (b == 'x'): self.startModule() # AKA square
        if (b == "y"): self.nextModule() # AKA triangle
        if (b == 'select'): self.quit()

    def ctrlCmd(self, args):
        cmd = args[0]
        del args[0]
        if cmd == 'drive':
            return self.drive.ctrlCmd(args)
        elif cmd == 'dist':
            return self.dist.ctrlCmd(args)
        elif cmd == 'servo':
            return self.servo.ctrlCmd(args)
        elif cmd == 'quit':
            self.quit()
        elif cmd == 'nextModule':
            return self.nextModule()
