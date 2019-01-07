#
# Driving in a line test - angle 
#


import threading
import time
import math

class Testline(threading.Thread):

    def __init__(self,robot):
        
        threading.Thread.__init__(self)
        self.robot = robot
        self.camera = robot.get_camera() 
        
    def run(self):
        self.robot.logMsg("Run testline module")
        self.robot.drive.setSpeedFactor(3.0)
        self.robot.update()

        self.robot.turtle.forwardDist(200)
        time.sleep(10)
        #self.robot.turtle.turnLeft()
        self.robot.turtle.turnDegrees(-90)
        time.sleep(1)
        #self.robot.turtle.turnLeft()
        self.robot.turtle.turnDegrees(90)
        time.sleep(1)
        self.robot.turtle.turnDegrees(2.5)
        time.sleep(1)
        self.robot.turtle.forward(5)
        self.robot.turtle.stop()
        time.sleep(1)
        self.robot.turtle.forward(5)
        self.robot.turtle.stop()
        time.sleep(30)
        
        elapsed = 0
        ad = 90
        ar = math.pi*ad/180.
        self.robot.logMsg("Starting to drive at an angle of: %d deg" % ad)
        ef0 = self.robot.drive.front.readEncoders()
        eb0 = self.robot.drive.back.readEncoders()
        self.robot.logMsg("t(0): Front encoders: %d , %d" % (ef0[0],ef0[1]))
        self.robot.logMsg("t(0): Rear encoders: %d , %d" % (eb0[0],eb0[1]))
        self.robot.drive.setDrive(1.0,ar)
        delta=0.5
        time.sleep(delta)
        elapsed+=delta
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        efd = (ef0[0]-ef[0],ef0[1]-ef[1])
        ebd = (eb0[0]-eb[0],eb0[1]-eb[1])
        ef0 = ef
        eb0 = eb
        
        self.robot.logMsg("t(%2.1f): Front encoders delta: %d , %d" % (elapsed,efd[0],efd[1]))
        self.robot.logMsg("t(%2.1f): Rear encoders delta: %d , %d" % (elapsed,ebd[0],ebd[1]))

        self.robot.logMsg("Drive in straight line")
        self.robot.drive.setDriveXY(1.0,0)
        delta=0.5
        time.sleep(delta)
        elapsed+=delta
        
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        efd = (ef0[0]-ef[0],ef0[1]-ef[1])
        ebd = (eb0[0]-eb[0],eb0[1]-eb[1])
        ef0 = ef
        eb0 = eb
        self.robot.logMsg("t(%2.1f): Front encoders delta: %d , %d" % (elapsed,efd[0],efd[1]))
        self.robot.logMsg("t(%2.1f): Rear encoders delta: %d , %d" % (elapsed,ebd[0],ebd[1]))

        
        self.robot.logMsg("Correct back by -%d deg" % ad)
        self.robot.drive.setDrive(1.0,-ar)

        delta=0.5
        time.sleep(delta)
        elapsed+=delta
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        efd = (ef0[0]-ef[0],ef0[1]-ef[1])
        ebd = (eb0[0]-eb[0],eb0[1]-eb[1])
        ef0 = ef
        eb0 = eb
        
        self.robot.logMsg("t(%2.1f): Front encoders delta: %d , %d" % (elapsed,efd[0],efd[1]))
        self.robot.logMsg("t(%2.1f): Rear encoders delta: %d , %d" % (elapsed,ebd[0],ebd[1]))

        
        self.robot.logMsg("And back to straight line")
        self.robot.drive.setDriveXY(1.0,0)
        delta=1
        elapsed+=delta
        time.sleep(delta)
        
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        efd = (ef0[0]-ef[0],ef0[1]-ef[1])
        ebd = (eb0[0]-eb[0],eb0[1]-eb[1])
        ef0 = ef
        eb0 = eb
        self.robot.logMsg("t(%2.1f): Front encoders delta: %d , %d" % (elapsed,efd[0],efd[1]))
        self.robot.logMsg("t(%2.1f): Rear encoders delta: %d , %d" % (elapsed,ebd[0],ebd[1]))

        
        self.robot.drive.stop()
        self.robot.logMsg("Stopping")
        
        
        self.robot.next_module(True)
        exit()


if __name__ == "__main__":
    from Camera import Camera
    camera = Camera()
    time.sleep(2)
    camera.stop()

