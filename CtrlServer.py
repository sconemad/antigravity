# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# CtrlServer - Server to allow control via UNIX socket (/tmp/robot)
#

import asyncio

from Drive import Drive
from Echo import Echo

path = '/tmp/robot'
count = 0

class CtrlProtocol(asyncio.Protocol):
    
    def __init__(self, ctrl, bot):
        self.ctrl = ctrl
        self.bot = bot

    def logMsg(self, msg):
        self.bot.logMsg("CtrlClient [%d] %s" % (self.id, msg))
        
    def connection_made(self, transport):
        global count
        count = count + 1
        self.transport = transport
        self.id = count
        self.logMsg("Connected")
        self.bot.drive.setSpeedFactor(1)
        
    def data_received(self, data):
        lines = data.decode().split('\n')
        for line in lines:
            args = line.split()
            if len(args)>0:
                self.logMsg(args)
                ret = self.ctrl.handleCmd(args)
                if ret:
                    self.logMsg(ret)
                    self.transport.write(("%s\n"%(str(ret))).encode())
        
    def eof_received(self):
        self.logMsg("Disconnected")
        self.bot.drive.stop()

class CtrlServer:
    
    def __init__(self, bot):
        self.bot = bot
        loop = asyncio.get_event_loop()
        c = loop.create_unix_server(
            lambda: CtrlProtocol(self, bot), path=path)
        self.server = loop.run_until_complete(c)
        self.bot.logMsg("CtrlServer listening on %s" % (path))

    def handleCmd(self, args):
        cmd = args[0]
        if cmd == 'setDrive':
            speed = float(args[1])
            angle = float(args[2])
            self.bot.drive.setDrive(speed,angle)

        elif cmd == 'getEcho':
            sensor = args[1]
            if sensor == 'C':
                return self.bot.echo.getDistance(Echo.ECHO_CENTRE)
            elif sensor == 'L':
                return self.bot.echo.getDistance(Echo.ECHO_LEFT)
            elif sensor == 'R':
                return self.bot.echo.getDistance(Echo.ECHO_RIGHT)
            else:
                return 0
