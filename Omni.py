import os
from Module import Module

class Omni(Module):

    def __init__(self, bot):
        Module.__init__(self, bot, "Omni")
        self.Running_p = False

    def start(self):
        self.logMsg("Running Omni...")
        self.Running_p = True
        os.system("~/bin/omni.sh")
        self.Running_p = False
        
    def getStatus(self):
        if self.Running_p is False:
            return "Stopped"
        else:
            return "Running"
