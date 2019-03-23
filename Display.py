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
        
    def timer(self, args):
        self.tick = self.tick + 1
        flash = self.tick % 2

        # Do the voltage bar
        v = self.bot.getBatteryVoltage()
        backlight.graph_set_led_state(5, v >= 10.5 or (v > 10 and flash))
        backlight.graph_set_led_state(4, v >= 11.5 or (v > 11 and flash))
        backlight.graph_set_led_state(3, v >= 12.5 or (v > 12 and flash))
        backlight.graph_set_led_state(2, v >= 13.5 or (v > 13 and flash))
        backlight.graph_set_led_state(1, v >= 14.5 or (v > 14 and flash))
        backlight.graph_set_led_state(0, v >= 15.5 or (v > 15 and flash))
        
        c = [')','|','(','|'][self.tick % 4]
        lcd.set_cursor_position(15,0)
        lcd.write(c)

        lcd.set_cursor_position(0,1)
        mod = self.bot.getModule()
        lcd.write("< %-12s >" % (mod.name))
        lcd.set_cursor_position(0,2)
        lcd.write("%-16s" % (mod.getStatus()))
    
        self.bot.setTimer(0.5, self.timer)

