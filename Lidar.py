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
from Module import Module

class Lidar(Module):

    # Measurement timing budget, see:
    # https://github.com/pololu/vl53l0x-arduino/blob/master/examples/Single/Single.ino
    MTB = 33000

    DIST_CENTRE = 1
    DIST_LEFT = 2
    DIST_RIGHT = 3

    I2C_MUX_ADDR = 0x72
    I2C_MUX_LEFT = 5
    I2C_MUX_RIGHT = 7
    I2C_MUX_CENTRE = 6
    
    def __init__(self, bot):
        super().__init__(bot, "Distance")
        self.bot = bot
        GPIO.setmode(GPIO.BCM)
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Init the sensors
        self._select(self.I2C_MUX_CENTRE)
        self.vl53_centre = adafruit_vl53l0x.VL53L0X(self.i2c)
        self.vl53_centre.measurement_timing_budget = self.MTB

        self._select(self.I2C_MUX_LEFT)
        self.vl53_left = adafruit_vl53l0x.VL53L0X(self.i2c)
        self.vl53_left.measurement_timing_budget = self.MTB

        self._select(self.I2C_MUX_RIGHT)
        self.vl53_right = adafruit_vl53l0x.VL53L0X(self.i2c)
        self.vl53_right.measurement_timing_budget = self.MTB

    def __del__(self):
        GPIO.cleanup()

    def _select(self, bus):
        self.i2c.writeto(self.I2C_MUX_ADDR, bytearray([int(2**bus)]))
        time.sleep(0.1)

    def getSensor(self, sensor):
        if (sensor == self.DIST_LEFT):
            self._select(self.I2C_MUX_LEFT)
            return self.vl53_left
        elif (sensor == self.DIST_RIGHT):
            self._select(self.I2C_MUX_RIGHT)
            return self.vl53_right
        else:
            self._select(self.I2C_MUX_CENTRE)
            return self.vl53_centre
        
    def getDistance(self, sensor):
        vl53 = self.getSensor(sensor)
        r = 9999
        try:
            r = vl53.range
        except:
            self.bot.logMsg("Failed")
        return r

    def getStatus(self):
        l = self.getDistance(self.DIST_LEFT)
        c = self.getDistance(self.DIST_CENTRE)
        r = self.getDistance(self.DIST_RIGHT)
        return "%-4d  %-4d  %4d" % (l,c,r)
        
    def ctrlCmd(self, args):
        cmd = args[0]
        if cmd == 'get':
            sensor = args[1]
            if sensor == 'L': return self.getDistance(self.DIST_LEFT)
            if sensor == 'R': return self.getDistance(self.DIST_RIGHT)
            if sensor == 'C': return self.getDistance(self.DIST_CENTRE)
            return 0
