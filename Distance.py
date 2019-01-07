#
# Drag race --- go forward until distance sensor says stop
#


import threading
import time
import math


class Distance(threading.Thread):

    def __init__(self,robot):
        
        threading.Thread.__init__(self)
        self.robot = robot
        self.camera = robot.get_camera() 

    def run(self):
        self.robot.logMsg("Run distance module")
        self.robot.drive.setSpeedFactor(1.0)
        # Ensure we definitely are going in the dir the sensor is facing
        # i.e. forward --- probably should disable flip temp ...
        self.robot.drive.setFlip(1)
        # TTD: also ensure head is at zero degrees
        self.robot.update()

        ef0 = self.robot.drive.front.readEncoders()
        eb0 = self.robot.drive.back.readEncoders()
        self.robot.logMsg("t(0): Front encoders: %d , %d" % (ef0[0],ef0[1]))
        self.robot.logMsg("t(0): Rear encoders: %d , %d" % (eb0[0],eb0[1]))
        self.robot.drive.setDrive(1.0,0)
        time.sleep(1)
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        self.robot.logMsg("t(1): Front encoders delta: %d , %d" % (ef[0]-ef0[0],ef[1]-ef0[1]))
        self.robot.logMsg("t(1): Rear encoders delta: %d , %d" % (eb[0]-eb0[0],eb[1]-eb0[1]))
        ef0 = ef
        eb0 = eb
        time.sleep(2)
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        self.robot.logMsg("t(2):  Front encoders delta: %d , %d" % (ef[0]-ef0[0],ef[1]-ef0[1]))
        self.robot.logMsg("t(2):  Rear encoders delta: %d , %d" % (eb[0]-eb0[0],eb[1]-eb0[1]))
        ef0 = ef
        eb0 = eb

        while True:
            time.sleep(2)
            ef0 = self.robot.drive.front.readEncoders()
            eb0 = self.robot.drive.back.readEncoders()
            self.robot.logMsg("t(0): Front encoders: %d , %d" % (ef0[0],ef0[1]))
            self.robot.logMsg("t(0): Rear encoders: %d , %d" % (eb0[0],eb0[1]))
                    
        
        
        self.robot.drive.stop()
        self.robot.logMsg("Stopping")
        
        dangerClose = False
        while not dangerClose:
            self.robot.drive.setDrive(1.0,0)
            d = self.robot.head.getDistance()
            self.robot.logMsg("Distance: %s" % d)
            if d < 200:
                self.robot.logMsg("WARNING: Close")
            # At a speed factor of 5, 30cm gives stop at 20 cm
            #                      3,  "                 14 cm
            # this is with a 0.5 sec lag
            # At a speed factor of 1, 60 cm gives a stop at 55 cm
            #  => ON WOOD!! Takes longer on carpet ?!?
            # On carpet, sf=1, 120 cm gives a stop at 35 cm
            if d < 120:
                self.robot.logMsg("WARNING: Danger Close")
                dangerClose = True
        self.robot.logMsg("Stopping motors")
        self.robot.drive.stop()
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.front.readEncoders()
        self.robot.logMsg("t(x):  Front encoders delta: %d , %d" % (ef[0]-ef0[0],ef[1]-ef0[1]))
        self.robot.logMsg("t(x):  Rear encoders delta: %d , %d" % (eb[0]-eb0[0],eb[1]-eb0[1]))

        
        self.robot.next_module(True)
        exit()

        

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

