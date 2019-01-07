#!/usr/bin/python

#---------------------------------------------
# VNCbot drive interface : Turtle-mode
#

#import math
import time
from Bot import Bot
#from MD25 import MD25

import Drive

class Turtle :
    def __init__(self, bot):
        self.bot = bot
#        self.front = MD25(0x58,1)
#        self.back = MD25(0x59,1)
#        self.ls = 0
#        self.rs = 0
        #self.turnCorrectionFactor=0.915 # See Calibrate TTD GET THIS FROM ROBOT
        self.distCorrectionFactor=1 # Just in case
        self.debug = False
        self.verbose = True
        
    def forward(self,timeSeconds):
        self.bot.logMsg(">>> Turtle starting forward move for %d" % int(timeSeconds))

        self.bot.drive.setFlip(1)
        self.bot.drive.setDriveXY(0,1)
        time.sleep(timeSeconds)
        self.stop()
        self.bot.logMsg("<<< Turtle stopping forward (time)")

        
    def forwardDist(self,distanceCM):
        # MD25 has:
            
        # max speed 200 rpm
        # PI * 0.1 * 200 / 60 = 1.047 m/s
        # wheel dia: 0.1m
        # wheel rotation covers: 0.3142m
        # wheel centre to centre axis in horiz plane: 0.1305m
        # Arc length for 90deg turn: 0.2050m
        #
        # 360 clicks per wheel rotation
        # 234 clicks per 90 deg

        
        ################
        # Ah, poo - this might be why we needed a correction factor!  typo
        # 264 clicks = 90 dec => 5 deg is 13 clicks 


        correctionfactor=self.bot.distCorrectionFactor
        nt=0.6361 # No of turns to do to get 0.200m
        c=360*nt*correctionfactor
        c=int(round(c*distanceCM/20))
        
        
        encoderError=1000 # We ignore deltas above this


        self.bot.logMsg(">>> Turtle starting forward move for %dcm (%d clicks)" % (int(distanceCM), c))

        
        ef0 = self.bot.drive.front.readEncoders()
        eb0 = self.bot.drive.back.readEncoders()
        ea0 = ((ef0[0]+eb0[0])/2., (ef0[1]+eb0[1])/2.)
        self.bot.logMsg("t(0): Encoder Front: 0=%d, 1=%d" % (ef0[0],ef0[1]))
        self.bot.logMsg("t(0): Encoder Back: 0=%d, 1=%d" % (eb0[0],eb0[1]))
        self.bot.logMsg("t(0): Encoder avg: 0=%3.2f 1=%3.2f" % (ea0[0],ea0[1]))


        # Due to the crazy values we sometimes got during turning, 
        #  wait until 3 of the 4 wheels have reached the target; or avg for both is ok
        self.bot.drive.setDriveXY(0,1.0) # Forward, in terms of Flip mode
        moving=True
        while moving:
            ef = self.bot.drive.front.readEncoders()
            eb = self.bot.drive.back.readEncoders()
            ea = ((ef[0]+eb[0])/2., (ef[1]+eb[1])/2.)
            if self.debug:
                self.bot.logMsg("t(x): Encoder Front: 0=%d, 1=%d" % (ef[0],ef[1]))
                self.bot.logMsg("t(x): Encoder Back: 0=%d, 1=%d" % (eb[0],eb[1]))
                self.bot.logMsg("t(x): Encoder avg: 0=%3.2f 1=%3.2f" % (ea[0],ea[1]))

                
            ead = (abs(ea[0]-ea0[0]),abs(ea[1]-ea0[1]))
            if self.debug: # Debug instead of verbose, or at least low verbosity
                self.bot.logMsg("t(x+0.25): ---> abs avg delta: %3.2f,  %3.2f" % (ead[0], ead[1]))
            if ead[0]>c and ead[1]>c:
                if self.verbose:
                    self.bot.logMsg(" <<< t(stop): ---> abs avg delta: %3.2f,  %3.2f" % (ead[0], ead[1]))
                if False: #ead[0]>encoderError or ead[1]>encoderError:
                    self.bot.logMsg(" <<< WARNING: deltas too large to be believable; ignoring")
                else:
                    self.bot.logMsg(" <<< Reached distance count,  Stopping forward")
                    break 
        
        
        self.stop()        
        if self.verbose:
            self.bot.logMsg("Turtle Stopping")
        
        self.bot.logMsg("<<< Turtle stopping foward (dist)")

        
    def stop(self):
        self.bot.logMsg(" <<< Turtle stop >>>")
        self.bot.drive.stop()

    def turnLeft(self):
        # MD25 has:
            
        # max speed 200 rpm
        # PI * 0.1 * 200 / 60 = 1.047 m/s
        # wheel dia: 0.1m
        # wheel rotation covers: 0.3142m
        # wheel centre to centre axis in horiz plane: 0.1305m
        # Arc length for 90deg turn: 0.2050m
        #
        # 360 clicks per wheel rotation
        # 234 clicks per 90 deg

        
        ################
        # Ah, poo - this might be why we needed a correction factor!  typo
        # 264 clicks = 90 dec => 5 deg is 13 clicks 

        
        correctionfactor=self.bot.turnCorrectionFactor
        nt=1 # No of turns to do to get 90 deg
        c=264*nt*correctionfactor

        encoderError=1000 # We ignore deltas above this
        
        self.bot.logMsg(">>> Turtle starting left turn")
            
        ef0 = self.bot.drive.front.readEncoders()
        eb0 = self.bot.drive.back.readEncoders()
        ea0 = ((ef0[0]+eb0[0])/2., (ef0[1]+eb0[1])/2.)
        self.bot.logMsg("t(0): Encoder Front: 0=%d, 1=%d" % (ef0[0],ef0[1]))
        self.bot.logMsg("t(0): Encoder Back: 0=%d, 1=%d" % (eb0[0],eb0[1]))
        self.bot.logMsg("t(0): Encoder avg: 0=%3.2f 1=%3.2f" % (ea0[0],ea0[1]))

#            self.bot.drive.setDrive(1.0,0)
        self.bot.drive.setDriveXY(-1.0,0)
        turning=True
        while turning:
            ef = self.bot.drive.front.readEncoders()
            eb = self.bot.drive.back.readEncoders()
            ea = ((ef[0]+eb[0])/2., (ef[1]+eb[1])/2.)
            if self.debug:
                self.bot.logMsg("t(x+0.25): Encoder Front: 0=%d, 1=%d" % (ef[0],ef[1]))
                self.bot.logMsg("t(x+0.25): Encoder Back: 0=%d, 1=%d" % (eb[0],eb[1]))
                self.bot.logMsg("t(x+0.25): Encoder avg: 0=%3.2f 1=%3.2f" % (ea[0],ea[1]))

                
            ead = (abs(ea[0]-ea0[0]),abs(ea[1]-ea0[1]))
            if self.debug: # Debug instead of verbose, or at least low verbosity
                self.bot.logMsg("t(x+0.25): ---> abs avg delta: %3.2f,  %3.2f" % (ead[0], ead[1]))
            if ead[0]>c or ead[1]>c:
                if self.verbose:
                    self.bot.logMsg(" <<< t(stop): ---> abs avg delta: %3.2f,  %3.2f" % (ead[0], ead[1]))
                if ead[0]>encoderError or ead[1]>encoderError:
                    self.bot.logMsg(" <<< WARNING: deltas too large to be believable; ignoring")
                else:
                    self.bot.logMsg(" <<< Reached rotational count,  Stopping turn")
                    #turning=False
                    break 

        self.bot.drive.stop()
        if self.verbose:
            self.bot.logMsg("Stopped turning - Current turn target reached")
                

    def turnDegrees(self,angle):
    # 264 clicks = 90 dec => 5 deg is 13 clicks
        # Should only really support -90 =< x <= 0  and 0 >= x >= +90
        
        correctionfactor=self.bot.turnCorrectionFactor
        nt=1 # No of turns to do to get 90 deg
        c=264*nt*correctionfactor*(abs(angle))/90
        if angle<0:
            turnDirection=-1.0
        else:
            turnDirection=+1.0
        
        encoderError=1000 # We ignore deltas above this
        
        self.bot.logMsg(">>> Turtle starting turn of %d degrees" % int(round(angle)))
            
        ef0 = self.bot.drive.front.readEncoders()
        eb0 = self.bot.drive.back.readEncoders()
        ea0 = ((ef0[0]+eb0[0])/2., (ef0[1]+eb0[1])/2.)
        self.bot.logMsg("t(0): Encoder Front: 0=%d, 1=%d" % (ef0[0],ef0[1]))
        self.bot.logMsg("t(0): Encoder Back: 0=%d, 1=%d" % (eb0[0],eb0[1]))
        self.bot.logMsg("t(0): Encoder avg: 0=%3.2f 1=%3.2f" % (ea0[0],ea0[1]))

#            self.bot.drive.setDrive(1.0,0)
        # left angle is -tive; => setDriveXY(-1.0,0)
        # right angle is -tive; => setDriveXY(-1.0,0)

        self.bot.drive.setDriveXY(turnDirection,0)
        turning=True
        while turning:
            ef = self.bot.drive.front.readEncoders()
            eb = self.bot.drive.back.readEncoders()
            ea = ((ef[0]+eb[0])/2., (ef[1]+eb[1])/2.)
            if self.debug:
                self.bot.logMsg("t(x+0.25): Encoder Front: 0=%d, 1=%d" % (ef[0],ef[1]))
                self.bot.logMsg("t(x+0.25): Encoder Back: 0=%d, 1=%d" % (eb[0],eb[1]))
                self.bot.logMsg("t(x+0.25): Encoder avg: 0=%3.2f 1=%3.2f" % (ea[0],ea[1]))

                
            ead = (abs(ea[0]-ea0[0]),abs(ea[1]-ea0[1]))
            if self.debug: # Debug instead of verbose, or at least low verbosity
                self.bot.logMsg("t(x+0.25): ---> abs avg delta: %3.2f,  %3.2f" % (ead[0], ead[1]))
            if ead[0]>c or ead[1]>c:
                if self.verbose:
                    self.bot.logMsg(" <<< t(stop): ---> abs avg delta: %3.2f,  %3.2f" % (ead[0], ead[1]))
                if ead[0]>encoderError or ead[1]>encoderError:
                    self.bot.logMsg(" <<< WARNING: deltas too large to be believable; ignoring")
                else:
                    self.bot.logMsg(" <<< Reached rotational count,  Stopping turn")
                    #turning=False
                    break 

        self.bot.drive.stop()
        if self.verbose:
            self.bot.logMsg("Stopped turning - Current turn target reached")

            
        
#    def setSpeedFactor(self, speedFactor):
#        self.speedFactor = speedFactor
#        self.update()

    def run(self):
        "For testing only"
        self.forward(5)
        self.stop()

        self.bot.next_module(True)
        exit()


if __name__ == "__main__":
    from Camera import Camera
    camera = Camera()
    time.sleep(2)
    camera.stop()

