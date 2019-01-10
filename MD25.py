# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# MD25 - MD25 motor controller interface
#

import time
import Adafruit_GPIO.I2C as I2C

# ===========================================================================
# MD25 Class
# ===========================================================================

class MD25:

  i2c = None

  # Operating Modes
  __MD25_STANDARD                 = 0
  __MD25_NEGATIVE_SPEEDS          = 1
  __MD25_SPEED_AND_TURN           = 2
  __MD25_NEGATIVE_SPEEDS_AND_TURN = 3

  # MD25 Registers
  __MD25_SPEED_1 = 0
  __MD25_SPEED_2 = 1
  __MD25_ENC_1A = 2
  __MD25_ENC_1B = 3
  __MD25_ENC_1C = 4
  __MD25_ENC_1D = 5
  __MD25_ENC_2A = 6
  __MD25_ENC_2B = 7
  __MD25_ENC_2C = 8
  __MD25_ENC_2D = 9
  __MD25_BATTERY_VOLTAGE = 10
  __MD25_MOTOR_1_CURRENT = 11
  __MD25_MOTOR_2_CURRENT = 12
  __MD25_SOFTWARE_VERSION = 13
  __MD25_ACCELERATION = 14
  __MD25_MODE = 15
  __MD25_COMMAND = 16

  __MD25_RESET_ENCODER_REGISTERS = 0x20
  __MD25_DISABLE_AUTO_SPEED_REGULATION = 0x30
  __MD25_ENABLE_AUTO_SPEED_REGULATION = 0x31
  __MD25_DISABLE_2_SECOND_TIMEOUT = 0x32
  __MD25_ENABLE_2_SECOND_TIMEOUT = 0x33
  __MD25_CHANGE_I2C_ADDRESS_1 = 0xA0
  __MD25_CHANGE_I2C_ADDRESS_2 = 0xAA
  __MD25_CHANGE_I2C_ADDRESS_3 = 0xA5


  # Private Fields
  _enc_1a = 0
  _enc_1b = 0
  _enc_1c = 0
  _enc_1d = 0
  _enc_2a = 0
  _enc_2b = 0
  _enc_2c = 0
  _enc_2d = 0
  _battery_voltage = 0
  _motor_1_current = 0
  _motor_2_current = 0
  _software_revision = 0

  # Constructor
  def __init__(self, address=0x58, mode=1, debug=False):
    self.i2c = I2C.Device(address, busnum=1)
    self.address = address
    self.debug = debug
    #XXX mode not working as we don't actually set it!
    if ((mode < 0) | (mode > 3)): 
      if (self.debug): 
        print("Invalid Mode: Using STANDARD by default")
      self.mode = self.__MD25_STANDARD
    else:
      self.mode = mode

  def forward(self, speed=255):
    self.i2c.write8(self.__MD25_SPEED_1, speed)
    self.i2c.write8(self.__MD25_SPEED_2, speed)

  def stop(self):
    self.i2c.write8(self.__MD25_SPEED_1, 128)
    self.i2c.write8(self.__MD25_SPEED_2, 128)

  def turn(self, speed1=255, speed2=1):
    self.i2c.write8(self.__MD25_SPEED_1, speed1)
    self.i2c.write8(self.__MD25_SPEED_2, speed2)

  def readCurrents(self):
    "Reads motor current values"
    i1 = self.i2c.readS8(self.__MD25_MOTOR_1_CURRENT)
    i2 = self.i2c.readS8(self.__MD25_MOTOR_2_CURRENT)
    return (i1/10.0, i2/10.0)

  def readBatteryVoltage(self):
    "Reads voltage value"
    v = self.i2c.readU8(self.__MD25_BATTERY_VOLTAGE)
    return v/10.0

#  def readAndVerifyS(self,f):
#    "Helper function to help with diagnosing I2C read errors"
#    r = f
#    if self.deb
  
  def readEncoders(self):
    "Reads encoder data"
    retry=30
    while True:
      # Bit pants that a a function that returns a signed value
      # uses -1 as a failed indicator --- c.f. readS8 TTD -fix
      failed=""
      OK=True
      e1a = self.i2c.readS8(self.__MD25_ENC_1A)
      if self.debug: print("e1a:",e1a)
      if e1a==None:
        OK=False
        failed+="e1a "
      e1b = self.i2c.readU8(self.__MD25_ENC_1B)
      if self.debug: print("e1b:",e1b)
      if e1b==-1:
        OK=False
        failed+="e1b "
      e1c = self.i2c.readU8(self.__MD25_ENC_1C)
      if self.debug: print("e1c:",e1c)
      if e1c==-1:
        OK=False
        failed+="e1c "
      e1d = self.i2c.readU8(self.__MD25_ENC_1D)
      if self.debug: print("e1d:",e1d)
      if e1d==-1:
        OK=False
        failed+="e1d "
      e2a = self.i2c.readS8(self.__MD25_ENC_2A)
      if self.debug: print("e2a:",e2a)
      if e2a==None:
        OK=False
        failed+="e2a "
      e2b = self.i2c.readU8(self.__MD25_ENC_2B)
      if self.debug: print("e2b:",e2b)
      if e2b==-1:
        OK=False
        failed+="e2b "
      e2c = self.i2c.readU8(self.__MD25_ENC_2C)
      if self.debug: print("e2c:",e2c)
      if e2c==-1:
        OK=False
        failed+="e2c "
      e2d = self.i2c.readU8(self.__MD25_ENC_2D)
      if self.debug: print("e2d:",e2d)
      if e2d==-1:
        OK=False
        failed+="e2d "

      if OK:
        if self.debug: print("OK - continuing")
        break
      else:
        retry-=1

      if not retry:
        if self.debug: print("not retry")
        break
      else:
        print("MD25.readEncoders WARNING - read failure for:%s; retrying immediately" % failed)
        #print("MD25.readEncoders WARNING - read failure for:%s; retrying in 100ms" % failed)
        #time.sleep(0.100) # Hacky fix, maybe

    # Does Python have NaN?
    if OK:
      return (e1d + (256*e1c) + (65536*e1b)+(16777216*e1a),
              e2d + (256*e2c) + (65536*e2b)+(16777216*e2a))
    else:
      print("MD25.readEncoders: Aborting after retries exhausted.")
      return None
    
# max speed 200 rpm
# PI * 0.1 * 200 / 60 = 1.047 m/s
# wheel dia: 0.1m
# wheel rotation covers: 0.3142m
# wheel centre to centre axis in horiz plane: 0.1305m
# Arc length for 90deg turn: 0.2050m

# 360 clicks per wheel rotation
# 234 clicks per 90 deg
