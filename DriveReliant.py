#!/usr/bin/python

#---------------------------------------------
# Reliant Drive control
#

from Drive import Drive
import piconzero as pz

class DriveReliant(Drive) :
    def __init__(self, bot):
        super().__init__(bot)
        pz.init()
        rv = pz.getRevision()
        self.bot.logMsg('Picon zero v%d.%d' % (rv[0],rv[1]))

    def __del__(self):
        pz.cleanup()
        
    def updateMotorSpeeds(self):
        pz.setMotor(0, int(127*self.ls))
        pz.setMotor(1, int(127*self.rs))
