#!/usr/bin/python3

from adafruit_pca9685 import PCA9685

import time
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

x = 0
while True:
    x = x + 1
    kit.servo[0].angle = ((x*5) % 180)
    kit.servo[1].angle = ((x*10) % 180)
    time.sleep(0.1)

#p = PCA9685()

#p.set_all_pwm(
