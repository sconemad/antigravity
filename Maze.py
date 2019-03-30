import os
from Module import Module

class Maze(Module):

    def __init__(self, bot):
        Module.__init__(self, bot, "Maze")
        self.Running_p = False

    def start(self):
        self.logMsg("Running Maze...")
        self.Running_p = True
        os.system("~/antigravity/Maze/Maze -steps 30")
        self.Running_p = False
        
    def getStatus(self):
        if self.Running_p is False:
            return "Stopped"
        else:
            return "Running"
