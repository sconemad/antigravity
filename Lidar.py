# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# VL53L0X LIDAR sensors interface
#

import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_vl53l0x

class Lidar:

    # Measurement timing budget, see:
    # https://github.com/pololu/vl53l0x-arduino/blob/master/examples/Single/Single.ino
    MTB = 33000

    # I2C addresses and XSHUT pins for VL53L0X modules:
    DIST_CENTRE = 1
    DIST_CENTRE_ADDR = 0x29
    DIST_CENTRE_XSHUT = 15

    DIST_LEFT = 2
    DIST_LEFT_ADDR = 0x2a
    DIST_LEFT_XSHUT = 14

    DIST_RIGHT = 3
    DIST_RIGHT_ADDR = 0x2b
    DIST_RIGHT_XSHUT = 18

    def __init__(self, bot):
        self.bot = bot
        GPIO.setmode(GPIO.BCM)
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Disable all sensors
        self._disable(self.DIST_LEFT_XSHUT)
        self._disable(self.DIST_RIGHT_XSHUT)
        self._disable(self.DIST_CENTRE_XSHUT)

        # Enable and configure sensors one by one
        self.left = self._setup(self.DIST_LEFT_XSHUT, self.DIST_LEFT_ADDR)
        self.right = self._setup(self.DIST_RIGHT_XSHUT, self.DIST_RIGHT_ADDR)
        self.centre = self._setup(self.DIST_CENTRE_XSHUT, self.DIST_CENTRE_ADDR)
        
    def __del__(self):
        GPIO.cleanup()

    def _enable(self, xshut):
        GPIO.setup(xshut, GPIO.IN)
        time.sleep(0.1)
            
    def _disable(self, xshut):
        GPIO.setup(xshut, GPIO.OUT)
        GPIO.output(xshut, False)

    def _setup(self, xshut, addr):
        self._enable(xshut)
        vl53 = adafruit_vl53l0x.VL53L0X(self.i2c)
        vl53._write_u8(adafruit_vl53l0x._I2C_SLAVE_DEVICE_ADDRESS, addr)
        vl53 = adafruit_vl53l0x.VL53L0X(self.i2c, addr)
        vl53.measurement_timing_budget = self.MTB
        return vl53
        
    def getDistance(self, sensor):
        if sensor == self.DIST_LEFT: return self.left.range
        if sensor == self.DIST_RIGHT: return self.right.range
        if sensor == self.DIST_CENTRE: return self.centre.range
        return 0

    def ctrlCmd(self, args):
        cmd = args[0]
        if cmd == 'get':
            sensor = args[1]
            if sensor == 'L': return self.getDistance(self.DIST_LEFT)
            if sensor == 'R': return self.getDistance(self.DIST_RIGHT)
            if sensor == 'C': return self.getDistance(self.DIST_CENTRE)
            return 0
