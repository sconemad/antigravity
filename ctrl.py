#!/usr/bin/python3

# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# ctrl - Control client app which talks to CtrlServer via /tmp/robot
#

import os
import fcntl
import asyncio
import termios
import sys
import math

path = '/tmp/robot'
client = 0

class CtrlClient(asyncio.Protocol) :
    def connection_made(self, transport):
        global client
        client = self
        self.transport = transport
        print("Connected")

    def data_received(self, data):
        args = data.decode().split()
        print(args)
            
    def eof_received(self):
        global client
        client = 0
        print("Closed")
        
    def close(self):
        self.transport.close()
        
    def setDrive(self, speed, angle):
        self.transport.write(("drive set %f %f" % (speed, angle)).encode())

    def getEcho(self, sensor):
        self.transport.write(("echo get %s" % (sensor)).encode())

def reconnect():
    loop = asyncio.get_event_loop()
    a = loop.create_unix_connection(CtrlClient, path=path)
    loop.create_task(a)
        
def readkeys():
    ch_set = []
    ch = os.read(sys.stdin.fileno(), 1)
    while ch != None and len(ch) > 0:
        ch_set.append(ch[0])
        ch = os.read(sys.stdin.fileno(), 1)
    return ch_set;
        
def stdinEvent():
    k = readkeys()
    if client==0:
        reconnect()
        return
    if len(k)==1: # Normal keys
        if chr(k[0])==' ':
            client.setDrive(0,0)
        elif chr(k[0])=='1':
            client.getEcho('L')
        elif chr(k[0])=='2':
            client.getEcho('C')
        elif chr(k[0])=='3':
            client.getEcho('R')
            
    elif len(k)==3 and k[0]==27 and k[1]==91:
        if k[2]==65: # up
            client.setDrive(1, 0)
        if k[2]==66: # down
            client.setDrive(1, math.pi)
        if k[2]==68: # left
            client.setDrive(1, math.pi/2)
        if k[2]==67: # right
            client.setDrive(1, -math.pi/2)

try:
    print("AntiGravity robot control client")
    ots = termios.tcgetattr(sys.stdin)
    nts = termios.tcgetattr(sys.stdin)
    nts[3] = nts[3] & ~(termios.ECHO | termios.ICANON)
    nts[6][termios.VMIN] = 0
    nts[6][termios.VTIME] = 0 
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, nts)
    orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin.fileno(), stdinEvent)
    reconnect()
    loop.run_forever()
    
finally:
    if client: client.close()
    loop.close()
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, ots)
