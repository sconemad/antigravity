import threading
import numpy as np
import time
import math
from Module import Module

blue_lower_range = np.array([100,70,70])
blue_upper_range = np.array([135,255,255])

red1_lower_range = np.array([0,70,70])
red1_upper_range = np.array([10,255,255])
# Red is either side of 0 degrees - we could normalize this?
red2_lower_range = np.array([170,70,70])
red2_upper_range = np.array([180,255,255])

green_lower_range = np.array([45,120,120])
green_upper_range = np.array([75,255,255])

yellow_lower_range = np.array([25,160,160])
yellow_upper_range = np.array([35,255,255])


class Rainbow(threading.Thread, Module):

    def __init__(self, robot):
        threading.Thread.__init__(self)
        Module.__init__(self, robot, "Rainbow")
        self.robot = robot
        self.camera = robot.get_camera()
        self.dist = robot.dist
        # Create list of colours to visit - RBYG
        self.colours = [(red1_lower_range, red1_upper_range, red2_lower_range, red2_upper_range),
                        (blue_lower_range, blue_upper_range, np.empty, np.empty),
                        (yellow_lower_range, yellow_upper_range, np.empty, np.empty),
                        (green_lower_range, green_upper_range, np.empty, np.empty)]

    def run(self):
        self.camera.start()
        time.sleep(5)
        while not self.camera.ready:
            time.sleep(0.5)

        for colour in self.colours:
            # Initial distance
            self.start_distance = 9999
            while self.start_distance >= 8100:
                self.start_distance = self.dist.getDistance(self.dist.DIST_CENTRE)
                time.sleep(0.2)

            print("Turn {0}".format(self.start_distance))
            # Turn and check
            self.robot.drive.setDriveLR(0.05, -0.05)
            while not self.camera.find_colour(colour[0], colour[1], colour[2], colour[3]):
                time.sleep(0.02)
            self.robot.drive.stop()

            print("Found colour - Move forward")
            # Move forward until range ~ 100
            self.robot.drive.setDriveLR(0.05, 0.05)
            self.current_distance = self.start_distance
            while self.current_distance > 100:
                self.current_distance = self.dist.getDistance(self.dist.DIST_CENTRE)
                time.sleep(0.02)
                print("Distance is now {0}", self.current_distance)
            self.robot.drive.stop()

            print("Move back")            
            # Move back until range is ~ start_distance
            self.robot.drive.setDriveLR(-0.05, -0.05)
            while self.current_distance < self.start_distance:
                self.current_distance = self.dist.getDistance(self.dist.DIST_CENTRE)
                time.sleep(0.02)
            self.robot.drive.stop()

        self.robot.drive.stop()

    def stop(self):
        self.robot.drive.stop()
        self.camera.stop()

if __name__ == "__main__":
    from Camera import Camera
    camera = Camera()
    while not self.camera.ready:
        time.sleep(0.5)

    colours = [(red1_lower_range, red1_upper_range, red2_lower_range, red2_upper_range),
               (blue_lower_range, blue_upper_range, np.empty, np.empty),
               (yellow_lower_range, yellow_upper_range, np.empty, np.empty),
               (green_lower_range, green_upper_range, np.empty, np.empty)]
    while True:
        for colour in colours:
            if self.camera.find_colour(colour[0], colour[1], colour[2], colour[3]):
                index = colours.index(colour)
                if index == 0:
                    print("Found red")
                elif index == 1:
                    print("Found blue")
                elif index == 2:
                    print("Found yellow")
                elif index == 3:
                    print("Found green")
        time.sleep(0.25)

    camera.stop()
