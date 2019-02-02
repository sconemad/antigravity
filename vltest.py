# Simple demo of the VL53L0X distance sensor.
# Will print the sensed range/distance every second.
import time

import board
import busio

import adafruit_vl53l0x
import RPi.GPIO as GPIO

# Optionally adjust the measurement timing budget to change speed and accuracy.
# See the example here for more details:
#   https://github.com/pololu/vl53l0x-arduino/blob/master/examples/Single/Single.ino
# For example a higher speed but less accurate timing budget of 20ms:
#vl53.measurement_timing_budget = 20000
# Or a slower but more accurate timing budget of 200ms:
#vl53.measurement_timing_budget = 200000
# The default timing budget is 33ms, a good compromise of speed and accuracy.
MTB = 33000

DIST_CENTRE_ADDR = 0x29
DIST_CENTRE_XSHUT = 15

DIST_LEFT_ADDR = 0x2a
DIST_LEFT_XSHUT = 14

DIST_RIGHT_ADDR = 0x2b
DIST_RIGHT_XSHUT = 18

GPIO.setmode(GPIO.BCM)
i2c = busio.I2C(board.SCL, board.SDA)

def _enable(xshut):
    GPIO.setup(xshut, GPIO.IN)
    time.sleep(0.1)
    
def _disable(xshut):
    GPIO.setup(xshut, GPIO.OUT)
    GPIO.output(xshut, False)

def _setup(xshut, addr):
    _enable(xshut)
    vl53 = adafruit_vl53l0x.VL53L0X(i2c)
    vl53._write_u8(adafruit_vl53l0x._I2C_SLAVE_DEVICE_ADDRESS, addr)
    vl53 = adafruit_vl53l0x.VL53L0X(i2c, addr)
    vl53.measurement_timing_budget = MTB
    return vl53

# Disable all sensors
_disable(DIST_LEFT_XSHUT)
_disable(DIST_RIGHT_XSHUT)
_disable(DIST_CENTRE_XSHUT)

# Enable and configure sensors one by one
vl53_left = _setup(DIST_LEFT_XSHUT, DIST_LEFT_ADDR)
vl53_right = _setup(DIST_RIGHT_XSHUT, DIST_RIGHT_ADDR)
vl53_centre = _setup(DIST_CENTRE_XSHUT, DIST_CENTRE_ADDR)

# Main loop will read the range and print it every second.
while True:
    dl = vl53_left.range
    dr = vl53_right.range
    dc = vl53_centre.range
    print('Range: %-04d %-04d %-04d' % (dl, dc, dr))
