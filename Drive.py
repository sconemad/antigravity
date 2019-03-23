#!/usr/bin/python

#---------------------------------------------
# Drive interface
#

import math

from Bot import Bot

# Update time period (s)
T = 0.1

# Straight (i.e. infinite turn radius)
Straight = float('inf')

class Drive :

    def __init__(self, bot):
        self.bot = bot
        self.ls = 0
        self.rs = 0
        self.tls = 0
        self.trs = 0
        self.bot.loop.call_later(T, self.timer, [])

    def timer(self, f):
        tls = self.tls
        trs = self.trs
            
        # Save previous actual wheel speeds for comparison later
        pls = self.ls
        prs = self.rs

        # Calculate current turn radius, tr
        d = self.ls - self.rs
        tr = Straight
        if abs(d) > 0.01: tr = (self.ls + self.rs) / d

        # Calculate current v, target v and acceleration required
        v = self.ls + self.rs
        tv = tls + trs
        a = tv - v

        # Limit deceleration to stop it falling over
        dlim = 0.03
#        dlim = 1000.0
        if a < -dlim: 
            p = a / -dlim
            print("Limiting decel %f" % (p))
            self.ls = self.ls + (tls - self.ls) / p
            self.rs = self.rs + (trs - self.rs) / p
        else:
            self.ls = tls
            self.rs = trs

        if self.ls > 1.0: self.ls = 1.0
        elif self.ls < -1.0: self.ls = -1.0
        if self.rs > 1.0: self.rs = 1.0
        elif self.rs < -1.0: self.rs = -1.0
            
        if self.ls != pls or self.rs != prs:
            self.bot.logMsg('Drive: %.3f %.3f (tr=%f acc=%f)' % (self.ls, self.rs, tr, a))
        if self.ls != 0 or self.rs != 0 or pls != 0 or prs != 0:
            self.updateMotorSpeeds(self.ls, self.rs)
        self.bot.loop.call_later(T, self.timer, [])
        
    def updateMotorSpeeds(self, ls, rs):
        self.bot.logMsg('Drive: Not implemented')

    def stop(self):
        self.tls = 0.0
        self.trs = 0.0
        
    def halt(self):
        'Emergency stop (ignores any acceleration control)'
        self.tls = 0
        self.trs = 0
        self.ls = 0
        self.rs = 0
        self.updateMotorSpeeds(0,0)
        
    def setDriveLR(self, ls, rs):
        'Set motor speeds directly'
        self.tls = ls
        self.trs = rs

    def setDriveST(self, s, t):
        if t > 0:
            self.trs = s
            self.tls = s * (t-1) / (t+1)
        else:
            self.tls = s
            self.trs = s * (-t-1) / (-t+1)
        
    def setDriveXY(self, x, y):
        'Set motor speeds based on X/Y joystick position'
        speed = math.sqrt(x*x + y*y)
        angle = math.atan2(-x, y)
        
        ls = 0.0
        rs = 0.0
        if (angle >= 0 and angle <= math.pi/2):
            d = 1 - (4*angle/math.pi)
            ls = speed * d
            rs = speed
        elif (angle <= 0 and angle >= -math.pi/2):
            d = 1 + (4*angle/math.pi)
            ls = speed
            rs = speed * d
        elif (angle > math.pi/2):
            d = 1 + (4*((math.pi/2)-angle)/math.pi)
            rs = speed*d
            ls = -speed
        elif (angle < -math.pi/2):
            d = 5 - (4*((math.pi/2)-angle)/math.pi)
            rs = -speed
            ls = speed * d

        # Limit speeds
        if (ls > 1): ls = 1
        if (ls < -1): ls = -1
        if (rs > 1): rs = 1
        if (rs < -1): rs = -1
        
        self.tls = ls
        self.trs = rs
    
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
        if cmd == 'setXY': # setXY <x> <y>
            x = float(args[1])
            y = float(args[2])
            self.setDriveXY(x,y)
        elif cmd == 'setST': # set <speed> <turn-rad>
            s = float(args[1])
            t = float(args[2])
            self.setDriveST(s,t)
        elif cmd == 'getVoltage': # getVoltage
            return self.getBatteryVoltage()
        elif cmd == 'getCurrent': # getCurrent
            return self.getMotorCurrent()
