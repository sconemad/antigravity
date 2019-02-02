# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# JS - Joystick input handler
#

import os
import struct
import fcntl
import array
import asyncio
import glob

class JSCallback :
    def leftStick():
        pass
    def rightStick():
        pass
    def dpadEvent():
        pass
    def buttonEvent():
        pass

class JS :
    def __init__(self, cb):
        self.cb = cb
        devs = glob.glob("/dev/input/by-id/*-X-joystick")
        if len(devs) == 0:
            print('JS: No joystick detected')
            return
        dev = devs[0]
        print('JS: Opening js %s...' % dev)
        self.fd = open(dev, 'rb')

        # Set the fd non-blocking
        flag = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)

        # Get the device name.
        buf = array.array('B', [0] * 64)
        # JSIOCGNAME(len)
        fcntl.ioctl(self.fd, 0x80006a13 + (0x10000 * len(buf)), buf)
        js_name = buf.tostring()
        print('JS: Device name: %s' % js_name)

        # Get number of axes and buttons.
        buf = array.array('B', [0])
        fcntl.ioctl(self.fd, 0x80016a11, buf) # JSIOCGAXES
        num_axes = buf[0]

        buf = array.array('B', [0])
        fcntl.ioctl(self.fd, 0x80016a12, buf) # JSIOCGBUTTONS
        num_buttons = buf[0]

        # Get the axis map.
        buf = array.array('B', [0] * 0x40)
        fcntl.ioctl(self.fd, 0x80406a32, buf) # JSIOCGAXMAP

        for axis in buf[:num_axes]:
            axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self.axis_map.append(axis_name)
            self.axis_states[axis_name] = 0.0

        # Get the button map.
        buf = array.array('H', [0] * 200)
        fcntl.ioctl(self.fd, 0x80406a34, buf) # JSIOCGBTNMAP

        for btn in buf[:num_buttons]:
            btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.button_map.append(btn_name)
            self.button_states[btn_name] = 0

        print('JS: %d axes found: %s' % (num_axes, ', '.join(self.axis_map)))
        print('JS: %d buttons found: %s' % (num_buttons, ', '.join(self.button_map)))

        loop = asyncio.get_event_loop()
        loop.add_reader(self.fd, self.event)

    def event(self):
        while True:
            try: evbuf = self.fd.read(8)
            except: return
            if (evbuf == None): return

            try:
                time, value, type, number = struct.unpack('IhBB', evbuf)
            except: pass
            
            if type & 0x80:
                # Let's not send initial states to the callbacks
                return

            if type & 0x01:
                button = self.button_map[number]
                if button:
                    self.button_states[button] = value
                    self.cb.buttonEvent(button, value)

            if type & 0x02:
                axis = self.axis_map[number]
                if axis:
                    fvalue = value / 32767.0
                    self.axis_states[axis] = fvalue
                    if (axis == 'lx' or axis == 'ly'):
                        self.cb.leftStick(self.axis_states['lx'],
                                          -self.axis_states['ly'])
                    elif (axis == 'rx' or axis == 'ry'):
                        self.cb.rightStick(self.axis_states['rx'],
                                           -self.axis_states['ry'])
                    elif (axis == 'dx' or axis == 'dy'):
                        self.cb.dpadEvent(self.axis_states['dx'],
                                          -self.axis_states['dy'])    

    cb = 0
    fd = 0
    
    # Event callbacks
    leftStick = 0
    rightStick = 0
    dpadEvent = 0
    buttonEvent = 0
        
    axis_states = {}
    button_states = {}

    # These constants were borrowed from linux/input.h
    axis_names = {
        0x00 : 'lx',
        0x01 : 'ly',
        0x02 : 'rx',
        0x03 : 'z1',
        0x04 : 'z2',
        0x05 : 'ry',
        0x09 : 'gas',
        0x0a : 'brake',
        0x10 : 'dx',
        0x11 : 'dy',
    }

    button_names = {
        0x130 : 'a',
        0x131 : 'b',
        0x133 : 'x',
        0x134 : 'y',
        0x136 : 'tl',
        0x137 : 'tr',
        0x138 : 'tl2',
        0x139 : 'tr2',
        0x13a : 'select',
        0x13b : 'start',
        0x13c : 'mode',
        0x13d : 'thumbl',
        0x13e : 'thumbr',
    }

    axis_map = []
    button_map = []
