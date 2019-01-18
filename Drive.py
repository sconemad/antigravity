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

        # Direct mode lets you set the motor speeds directly
        if self.direct:
            self.bot.logMsg('Drive: %.3f %.3f [direct]' % (self.ls, self.rs))
            self.updateMotorSpeeds()
            return
        
        # Calculate left and right motor speeds from speed and angle
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
        self.bot.logMsg('Drive: %.3f %.3f  [FLIP=%d BIAS=%1.3f]' % (ls, rs, self.flip, self.biasCorrection))
        self.ls = ls
        self.rs = rs
        self.updateMotorSpeeds()

    def setSpeed(self, speed):
        self.speed = speed
        self.direct = 0
        self.update()

    def setAngle(self, angle):
        self.angle = angle
        self.direct = 0
        self.update()

    def setDrive(self, speed, angle):
        self.speed = speed
        self.angle = angle
        self.direct = 0
        self.update()
        
    def setDriveXY(self, x, y):
        self.speed = math.sqrt(x*x + y*y)
        self.angle = math.atan2(x, y)
        self.direct = 0
        self.update()
    
    def stop(self):
        self.speed = 0.0
        self.angle = 0.0
        self.direct = 0
        self.update()

    def setDriveLR(self, ls, rs):
        self.ls = ls
        self.rs = rs
        self.direct = 1
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
        self.update()
        
    def getMotorCurrent(self):
        c = self.md25.readCurrents()
        return (c[0]+c[1])

    def getBatteryVoltage(self):
        return self.md25.readBatteryVoltage()

    def ctrlCmd(self, args):
        cmd = args[0]
        if cmd == 'stop': # stop
            self.stop()
        if cmd == 'setLR': # setLR <lspeed> <rspeed>
            ls = float(args[1])
            rs = float(args[2])
            self.setDriveLR(ls,rs)
        elif cmd == 'set': # set <speed> <angle>
            speed = float(args[1])
            angle = float(args[2])
            self.setDrive(speed,angle)
        elif cmd == 'setSpeed': # setSpeed <speed>
            speed = float(args[1])
            self.setSpeed(speed)
        elif cmd == 'setAngle': # setAngle <angle>
            angle = float(args[1])
            self.setAngle(angle)
        elif cmd == 'setSpeedFactor': # setSpeedFactor <factor>
            sf = int(args[1])
            self.setSpeedFactor(sf)
        elif cmd == 'setFlip': # setFlip <0|1>
            flip = int(args[1])
            self.setFlip(flip)
    
    speedFactor = 1
    speed = 0.0
    angle = 0.0
    flip = 0
    direct = 0
