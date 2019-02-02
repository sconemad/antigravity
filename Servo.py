# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# Servo interface
#

from adafruit_servokit import ServoKit

class Servo:

    def __init__(self, bot):
        self.bot = bot
        self.kit = ServoKit(channels=16)

    def ctrlCmd(self, args):
        cmd = args[0]
        if cmd == 'set':
            servo = int(args[1])
            angle = int(args[2])
            self.kit.servo[servo].angle = angle
