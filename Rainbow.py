import threading
import numpy as np
import time
import math

blue_lower_range = np.array([90,70,70])
blue_upper_range = np.array([120,255,255])

red_lower_range = np.array([0,120,120])
red_upper_range = np.array([10,255,255])

green_lower_range = np.array([40,120,120])
green_upper_range = np.array([70,255,255])

yellow_lower_range = np.array([28,180,180])
yellow_upper_range = np.array([28,255,255])


class Rainbow(threading.Thread):

    def __init__(self,robot):

        threading.Thread.__init__(self)
        self.robot = robot
        self.camera = robot.get_camera() 
        self.colours = [(red_lower_range,red_upper_range),
                        (blue_lower_range,blue_upper_range),
                        (yellow_lower_range,yellow_upper_range),
                        (green_lower_range,green_upper_range)]
        self.robot.drive.setSpeedFactor(5.0)
        self.robot.drive.setFlip(0)

    def run(self):
        for colour in self.colours:
            found = False
            while not found:
                self.robot.drive.setSpeedFactor(5.0)
                self.robot.drive.setDrive(1,(math.pi / 2))
                found = self.camera.find_colour(colour[0],colour[1])
            self.robot.drive.stop()
            self.robot.drive.setSpeedFactor(5.0)
            self.robot.drive.setDrive(1.0,math.pi)
            time.sleep(2.2)
            self.robot.drive.setSpeedFactor(5.0)
            self.robot.drive.setDrive(1.0,0)
            time.sleep(2.2)
            self.robot.drive.stop()
                

        self.robot.drive.stop()

if __name__ == "__main__":
    from Camera import Camera
    camera = Camera()
    time.sleep(2)
    found = False
    self.robot.drive.flip(0)

    while not found:
        found = camera.find_colour(red_lower_range,red_upper_range)
        time.sleep(0.5)
    self.robot.drive.setSpeedFactor(5.0)
    self.robot.drive.setDrive(1.0,math.pi)
    time.sleep(1.7)
    self.robot.drive.setSpeedFactor(5.0)
    self.robot.drive.setDrive(1.0,0)
    time.sleep(1.7)
    self.robot.drive.stop()

    camera.stop()


