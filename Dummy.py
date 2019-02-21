import threading
import time
import math


class Dummy(threading.Thread):

    def __init__(self,robot):

        threading.Thread.__init__(self)
        self.robot = robot
#        self.camera = robot.get_camera() 
#        self.robot.drive.setSpeedFactor(5.0)
        

    def run(self):
        self.robot.logMsg("Run dummy module")
        self.robot.logMsg("dummy.run: sleeping for 3 sec")
        time.sleep(3)
        self.robot.next_module(True)
        # Boilerplate
        # self.robot.logMsg("Finished Auto Module:" + self.robot.modulemode)
        # self.robot.modulemode = "rainbow"
        # self.robot.currentmode = "Manual / " + self.robot.modulemode
        # self.robot.update()
        exit()

        
        # for colour in self.colours:
        #     found = False
        #     while not found:
        #         self.robot.drive.setSpeedFactor(5.0)
        #         self.robot.drive.setDrive(1,(math.pi / 2))
        #         found = self.camera.find_colour(colour[0],colour[1])
        #     self.robot.drive.stop()
        #     self.robot.drive.setSpeedFactor(5.0)
        #     self.robot.drive.setDrive(1.0,math.pi)
        #     time.sleep(2)
        #     self.robot.drive.setSpeedFactor(5.0)
        #     self.robot.drive.setDrive(1.0,0)
        #     time.sleep(2)
        #     self.robot.drive.stop()
                

        # self.robot.drive.stop()

if __name__ == "__main__":
    from Camera import Camera
    camera = Camera()
    time.sleep(2)
    camera.stop()

