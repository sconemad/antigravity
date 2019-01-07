#!/usr/bin/python

#---------------------------------------------
# Drive interface
#

import math

from Bot import Bot

class Drive :
    def __init__(self, bot):
        self.bot = bot
        self.ls = 0
        self.rs = 0
        
        # -tive makes go left when going forward eg -0.95
        # 0 (or 1) turns off
        # Factor / 1+/-delta; 0.95 => slow right motors by 5% to make move to right
        self.biasCorrection = 1
        self.biasCorrection = -0.99 # Still turns left going forward, but almost straight rev
        self.biasCorrection = 1.0 #  Turns slightly to right, mostly, for 3,2,1 speeds 20-Apr-2018 speedtests
        self.biasCorrection = -0.995 # At speed=1 is about 10 cm to right still over 7.2m
        self.biasCorrection = -0.75 # At speed=1  # GAH =>-tive is RIGHT
        self.biasCorrection = 0.75 # TEST!!!
        self.biasCorrection = 1 # 

    def updateMotorSpeeds(self):
        print('Drive: Not implemented')

    def update(self):
        "Update motors with the current drive settings"

        # Calculate left and right motor speeds
        speed = self.speed / self.speedFactor
        ls = 0.0
        rs = 0.0
        if (self.angle >= 0 and self.angle <= math.pi/2):
            d = 1 - (4*self.angle/math.pi)
            ls = speed * d
            rs = speed
        elif (self.angle <= 0 and self.angle >= -math.pi/2):
            d = 1 + (4*self.angle/math.pi)
            ls = speed
            rs = speed * d
        elif (self.angle > math.pi/2):
            d = 1 + (4*((math.pi/2)-self.angle)/math.pi)
            rs = speed*d
            ls = -speed
        elif (self.angle < -math.pi/2):
            d = 5 - (4*((math.pi/2)-self.angle)/math.pi)
            rs = -speed
            ls = speed * d
            

        
        # Limit speeds
        if (ls > 1): ls = 1
        if (ls < -1): ls = -1
        if (rs > 1): rs = 1
        if (rs < -1): rs = -1

        if (self.flip):
            tls = ls
            ls = -rs
            rs = -tls

        ####################################
        #
        # Correct for slippage/motor bias
        #
        # +tive means we want to turn more to the:
        #      - right when going forward (i.e reduce RHS motors)
        # (i.e in a straight line without the bias we are turning left going forward and
        #                                                         right when reversing,
        #                                                         from POV of md25)
        # -tive means we want to turn left when going forward (i.e. reduce LHS motors)
        if self.biasCorrection:
            if self.biasCorrection>0:
                rs = rs * self.biasCorrection
            else:
                ls = ls * abs(self.biasCorrection) 
        # NOTE: Flip=1 actually means go forward.  I think L/R are reversed by accident.
        # so we have this in the "wrong" place after the flip reversal
        # L/R in "abs" terms facing md25.  Even though md25 has fwd speeds -tive



            
            
        # Send to controllers
        self.bot.logMsg('SPEEDS: %.3f %.3f  [FLIP=%d BIAS=%1.3f]' % (ls, rs, self.flip, self.biasCorrection))
#        self.md25.turn(int(128+(127*rs)), int(128+(127*ls)))
        self.ls = ls
        self.rs = rs
        self.updateMotorSpeeds()

    def setSpeed(self, speed):
        self.speed = speed
        self.update()

    def setAngle(self, angle):
        self.angle = angle
        self.update()

    def setDrive(self, speed, angle):
        self.speed = speed
        self.angle = angle
        self.update()
        
    def setDriveXY(self, x, y):
        self.speed = math.sqrt(x*x + y*y)
        self.angle = math.atan2(x, y)
        self.update()
    
    def stop(self):
        self.speed = 0.0
        self.angle = 0.0
        self.update()

    def setSpeedFactor(self, speedFactor):
        self.speedFactor = speedFactor
        self.update()

    def incSpeedFactor(self):
        if (self.speedFactor < 5):
            self.setSpeedFactor(self.speedFactor + 1)
            
    def decSpeedFactor(self):
        if (self.speedFactor > 1):
            self.setSpeedFactor(self.speedFactor - 1)

    def setBiasCorrection(self,bc):
        "Left/right drive bias; -tive is move left; 0.95 is turn right by driving RHS @ 95%"
        # 0 <= bc <= 1; +0.05 means bias by 5% to right, i.e turn right to correct it going left
        # Mixing factors, bias and corrections into one confusing lump.
        # And it seems that driveXY and drive behave differently ? ?
        if bc<0:
            self.biasCorrection = -(1+bc)
        else:
            self.biasCorrection = 1-bc
        self.update()
        
    def setFlip(self, flip):
        self.flip = flip
        
    def getMotorCurrent(self):
        c = self.md25.readCurrents()
        return (c[0]+c[1])

    def getBatteryVoltage(self):
        return self.md25.readBatteryVoltage()
        
    speedFactor = 1
    speed = 0.0
    angle = 0.0
    flip = 0
