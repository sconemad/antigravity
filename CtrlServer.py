# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# CtrlServer - Server to allow control via UNIX socket (/tmp/robot)
#

import time
import asyncio

from Drive import Drive
from Echo import Echo

path = '/tmp/robot'
cnum = 0
cmax = 0

class CtrlProtocol(asyncio.Protocol):
    
    def __init__(self, ctrl, bot):
        self.ctrl = ctrl
        self.bot = bot

    def logMsg(self, msg):
        self.bot.logMsg("CtrlClient [%d] %s" % (self.id, msg))
        
    def connection_made(self, transport):
        global cnum
        global cmax
        cnum = cnum + 1
        cmax = cmax + 1
        self.transport = transport
        self.id = cmax
        self.logMsg("Connected")
        
    def data_received(self, data):
        lines = data.decode().split('\n')
        for line in lines:
            args = line.split()
            if len(args)>0:
                self.logMsg(args)
                ret = self.bot.ctrlCmd(args)
                if ret != None:
                    self.logMsg(ret)
                    self.transport.write(("%s\n"%(str(ret))).encode())
    def eof_received(self):
        global cnum
        cnum = cnum - 1
        self.logMsg("Disconnected")
        if cnum == 0: self.bot.drive.stop()

class CtrlServer:
    
    def __init__(self, bot):
        self.bot = bot
        loop = asyncio.get_event_loop()
        c = loop.create_unix_server(
            lambda: CtrlProtocol(self, bot), path=path)
        self.server = loop.run_until_complete(c)
        self.bot.logMsg("CtrlServer listening on %s" % (path))
