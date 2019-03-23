# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# Module - Module base class
#

import os
import datetime

class Module:
    
    def __init__(self, bot, name):
        self.bot = bot
        self.name = name

    def logMsg(self, msg):
        self.bot.logMsg('%s: %s' % (self.name, msg))

    def start(self):
        self.logMsg('start method not implemented')

    def stop(self):
        self.logMsg('stop method not implemented')

    def getStatus(self):
        return ""
        
    def handleLeft(self):
        return
        
    def handleRight(self):
        return
    
    def handleSelect(self):
        return
    
