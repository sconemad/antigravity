# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# Echo sensors interface
#
# Includes code from hcsr04.py from 4tronix with the following copyright:
#
# Created by Gareth Davies, Mar 2016
# Copyright 4tronix
#
# This code is in the public domain and may be freely copied and used
# No warranty is provided or implied

import RPi.GPIO as GPIO
import time

class Echo:

    # Pin assignments for hc-sr04 sensors:
    ECHO_CENTRE = 7
    ECHO_LEFT = 12
    ECHO_RIGHT = 11

    def __init__(self, bot):
        self.bot = bot
        self.maxDist = 1000
        GPIO.setwarnings(False)
#        GPIO.setmode(GPIO.BOARD)

    def __del__(self):
        GPIO.cleanup()

    def getDistance(self, echoPin):
        GPIO.setup(echoPin, GPIO.OUT)
        # Send 10us pulse to trigger
        GPIO.output(echoPin, False)
        time.sleep(0.00001)
        GPIO.output(echoPin, True)
        timeout = self.maxDist / 170000.0
        start = time.time()
        count=time.time()
        GPIO.setup(echoPin,GPIO.IN)
        while GPIO.input(echoPin)==0 and time.time()-count<timeout:
            start = time.time()
        count=time.time()
        stop=count
        while GPIO.input(echoPin)==1 and time.time()-count<timeout:
            stop = time.time()
        # Calculate pulse length
        elapsed = stop-start
        # Distance pulse travelled in that time is time
        # multiplied by the speed of sound (mm/s)
        distance = elapsed * 340000
        # That was the distance there and back so halve the value
        distance = int(distance / 2)
        if (distance > self.maxDist): distance = self.maxDist;
        GPIO.setup(echoPin, GPIO.OUT)
        GPIO.output(echoPin, True)
        return distance

    def ctrlCmd(self, args):
        cmd = args[0]
        if cmd == 'get':
            sensor = args[1]
            if sensor == 'C':
                return self.getDistance(Echo.ECHO_CENTRE)
            elif sensor == 'L':
                return self.getDistance(Echo.ECHO_LEFT)
            elif sensor == 'R':
                return self.getDistance(Echo.ECHO_RIGHT)
            elif sensor == 'P':
                return self.getDistance(38)
            else:
                return 0
