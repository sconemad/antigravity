# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# DriveMD25 - Drive controller using MD25
#

from Drive import Drive
from MD25 import MD25

class DriveMD25(Drive):

    def __init__(self, bot):
        super().__init__(bot)
        self.md25 = MD25(0x59,1)
#        self.md25 = MD25(0x58,1)
        self.md25.readBatteryVoltage()
            
    def updateMotorSpeeds(self, ls, rs):
        l = int(128+(127*-ls))
        r = int(128+(127*-rs))
        try:
            self.md25.turn(l,r)
        except:
            self.bot.logMsg("Went wrong")

    def getMotorCurrent(self):
        c = self.md25.readCurrents()
        return (c[0]+c[1])

    def getBatteryVoltage(self):
        return self.md25.readBatteryVoltage()
