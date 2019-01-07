#======================================================================
#
# Python Module to handle an HC-SR04 Ultrasonic Module on a single Pin
# Aimed at use on Picon Zero
#
# Created by Gareth Davies, Mar 2016
# Copyright 4tronix
#
# This code is in the public domain and may be freely copied and used
# No warranty is provided or implied
#
#======================================================================

import RPi.GPIO as GPIO
import time

#======================================================================
# General Functions
#
def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

def cleanup():
    GPIO.cleanup()

#======================================================================

#======================================================================
# UltraSonic Functions
#
# getDistance(). Returns the distance in cm to the nearest reflecting object. 0 == no object
def getDistance(echoPin, maxDist):
    GPIO.setup(echoPin, GPIO.OUT)
    # Send 10us pulse to trigger
    GPIO.output(echoPin, False)
    time.sleep(0.00001)
    GPIO.output(echoPin, True)
    timeout = maxDist / 17000.0
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
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34000
    # That was the distance there and back so halve the value
    distance = distance / 2
    if (distance > maxDist): distance = maxDist;

    GPIO.setup(echoPin, GPIO.OUT)
    GPIO.output(echoPin, True)
    return distance

# End of UltraSonic Functions    
#======================================================================

