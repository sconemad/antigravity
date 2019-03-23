import os
from Module import Module

class Shutdown(Module):

    def __init__(self, bot):
        Module.__init__(self, bot, "Shutdown")

    def start(self):
        self.logMsg("Shutting down...")
        os.system("sudo halt")

    def getStatus(self):
        return "Are you sure?"
