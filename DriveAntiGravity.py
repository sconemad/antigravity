#!/usr/bin/python

#---------------------------------------------
# AntiGravity Drive control
#

from Drive import Drive
from MD25 import MD25

class DriveAntiGravity(Drive) :
    def __init__(self, bot):
        super().__init__(bot)
        self.md25 = MD25(0x58,1)
        self.md25.readBatteryVoltage()
            
    def updateMotorSpeeds(self):
        self.md25.turn(int(128+(127*self.rs)), int(128+(127*self.ls)))

    def getMotorCurrent(self):
        c = self.md25.readCurrents()
        return (c[0]+c[1])

    def getBatteryVoltage(self):
        return self.md25.readBatteryVoltage()
