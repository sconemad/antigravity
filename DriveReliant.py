#!/usr/bin/python

#---------------------------------------------
# Reliant Drive control
#

from Drive import Drive
import piconzero as pz

class DriveReliant(Drive) :
    def __init__(self, bot):
        super().__init__(bot)
        rv = pz.getRevision()
        bot.logMsg('Picon zero v%d.%d' % (rv[0],rv[1]))

    def updateMotorSpeeds(self):
        pz.setMotor(0, int(128+(127*self.ls)))
        pz.setMotor(1, int(128+(127*self.rs)))
