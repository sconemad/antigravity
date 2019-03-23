import threading
import time
import math
from Module import Module

class Dummy(Module, threading.Thread):

    def __init__(self, bot):
        threading.Thread.__init__(self)
        Module.__init__(self, bot, "Module")

    def run(self):
        self.bot.logMsg("Run dummy module")
        self.bot.logMsg("dummy.run: sleeping for 3 sec")
        time.sleep(3)
        self.bot.next_module(True)
        # Boilerplate
        # self.robot.logMsg("Finished Auto Module:" + self.robot.modulemode)
        # self.robot.modulemode = "rainbow"
        # self.robot.currentmode = "Manual / " + self.robot.modulemode
        # self.robot.update()
        exit()
