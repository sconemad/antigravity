# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# Display interface using Pimoroni Display-o-tron HAT
#

import os
import sys
import time
import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav
    
class Display:

    def __init__(self, bot):
        self.bot = bot
        lcd.set_cursor_position(0,0)
        lcd.write("  AntiGravity")
        backlight.rgb(255,255,255)
        backlight.graph_off()
        backlight.graph_set_led_duty(0,1)
        self.tick = 0
        self.graph = 0
        self.count = 0
        self.timer([])
        
        @nav.on(nav.LEFT)
        def handleLeft(ch, evt):
            self.bot.prevModule()

        @nav.on(nav.RIGHT)
        def handleRight(ch, evt):
            self.bot.nextModule()

        @nav.on(nav.BUTTON)
        def handleButton(ch, evt):
            self.bot.startModule()

        @nav.on(nav.CANCEL)
        def handleButton(ch, evt):
            self.bot.stopModule()

    def showSpeedFactor(self, factor):
        self.graph = 1
        self.speedFactor = factor
        self.count = 4

    def showFlip(self, flip):
        self.graph = 2
        self.flip = flip
        self.count = 4
            
    def timer(self, args):
        self.tick = self.tick + 1
        flash = self.tick % 2

        if self.graph == 1:
            # Do the speed factor
            backlight.graph_set_led_state(5, flash and self.speedFactor > 0)
            backlight.graph_set_led_state(4, flash and self.speedFactor > 1)
            backlight.graph_set_led_state(3, flash and self.speedFactor > 2)
            backlight.graph_set_led_state(2, flash and self.speedFactor > 3)
            backlight.graph_set_led_state(1, flash and self.speedFactor > 4)
            backlight.graph_set_led_state(0, flash and self.speedFactor > 5)
        elif self.graph == 2:
            # Do the flip
            if self.flip:
                backlight.graph_set_led_state(0, self.count == 5)
                backlight.graph_set_led_state(1, self.count == 4)
                backlight.graph_set_led_state(2, self.count == 3)
                backlight.graph_set_led_state(3, self.count == 2)
                backlight.graph_set_led_state(4, self.count == 1)
                backlight.graph_set_led_state(5, self.count == 0)
            else:
                backlight.graph_set_led_state(5, self.count == 5)
                backlight.graph_set_led_state(4, self.count == 4)
                backlight.graph_set_led_state(3, self.count == 3)
                backlight.graph_set_led_state(2, self.count == 2)
                backlight.graph_set_led_state(1, self.count == 1)
                backlight.graph_set_led_state(0, self.count == 0)
        else:
            # Do the voltage bar
            v = self.bot.getBatteryVoltage()
            backlight.graph_set_led_state(5, v >= 10.5 or (v > 10 and flash))
            backlight.graph_set_led_state(4, v >= 11.5 or (v > 11 and flash))
            backlight.graph_set_led_state(3, v >= 12.5 or (v > 12 and flash))
            backlight.graph_set_led_state(2, v >= 13.5 or (v > 13 and flash))
            backlight.graph_set_led_state(1, v >= 14.5 or (v > 14 and flash))
            backlight.graph_set_led_state(0, v >= 15.5 or (v > 15 and flash))

        if self.count > 0: self.count = self.count - 1
        if self.count == 0: self.graph = 0
                    
        c = [')','|','(','|'][self.tick % 4]
        lcd.set_cursor_position(15,0)
        lcd.write(c)

        lcd.set_cursor_position(0,1)
        mod = self.bot.getModule()
        lcd.write("< %-12s >" % (mod.name))
        lcd.set_cursor_position(0,2)
        lcd.write("%-16s" % (mod.getStatus()))
    
        self.bot.setTimer(0.5, self.timer)

