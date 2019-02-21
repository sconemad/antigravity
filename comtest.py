#!/usr/bin/python3

import time
from MD25 import MD25
from Lidar import Lidar
from Bot import Bot

bot = Bot()
lidar = Lidar(bot)
md25 = MD25(0x59)

l = 0
c = 0
r = 0
x = 127
while True:
    x = x + 2

    v = md25.readBatteryVoltage()
    l = lidar.getDistance(lidar.DIST_LEFT)
    c = lidar.getDistance(lidar.DIST_CENTRE)
    r = lidar.getDistance(lidar.DIST_RIGHT)
    print("%d: %d %d %d v=%f" % (x,l,c,r,v))
    
    md25.forward(120 + (x % 16))
#    md25.forward(x % 255)
