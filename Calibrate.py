#
# Test calibration - straight line / rotate around
#

# If battery voltage =0 means we're charging ... can't measure shaft encoders so
#  should refuse to run as otherwise just will be displaying stuff on screen with no stop


import threading
import time
import math


class Calibrate(threading.Thread):

    def __init__(self,robot):
        
        threading.Thread.__init__(self)
        self.robot = robot
        self.camera = robot.get_camera() 
        self.debug = False
        self.verbose = True
        #self.turnCorrectionFactor=0.95
        #self.turnCorrectionFactor=0.98 # This was perfect on Thur - 70% charge? ?
        # 100% charge is approx 0.92 20-APR-2018
        #self.turnCorrectionFactor=0.92 # Slight overturning
#        self.turnCorrectionFactor=self.robot.turnCorrectionFactor

        self.biasCorrection=-0.005
        self.biasCorrectionDelta=0.005
        
        
    def setBiasCorrection(self,bias):
        self.biasCorrection=bias
        self.robot.drive.setBiasCorrection(bias) # TTD: right thing to do? 

        
    def setBiasCorrectionDelta(self,delta):
        self.biasCorrectionDelta=delta
        
    def turn(self):
    # 264 clicks = 90 dec => 5 deg is 13 clicks

        correctionfactor=self.robot.turnCorrectionFactor
        nt=1 # No of turns to do to get 90 deg
        c=264*nt*correctionfactor

        encoderError=1000 # We ignore deltas above this
        
        self.robot.logMsg("Starting loop")
        lc=1 # Loop counters.  In python?  Yes, I'm mad
        nr=8 # Iterations/number of rotations below to do
        # This is a complete mess...       
        while True: # looping
            self.robot.logMsg(">>> Starting 90 DEG TURN x [%d of %d]" % (lc, nr))
            
            ef0 = self.robot.drive.front.readEncoders()
            eb0 = self.robot.drive.back.readEncoders()
            ea0 = ((ef0[0]+eb0[0])/2., (ef0[1]+eb0[1])/2.)
            self.robot.logMsg("t(0): Encoder Front: 0=%d, 1=%d" % (ef0[0],ef0[1]))
            self.robot.logMsg("t(0): Encoder Back: 0=%d, 1=%d" % (eb0[0],eb0[1]))
            self.robot.logMsg("t(0): Encoder avg: 0=%3.2f 1=%3.2f" % (ea0[0],ea0[1]))

#            self.robot.drive.setDrive(1.0,0)
            self.robot.drive.setDriveXY(-1.0,0)
            turning=True
            while turning:
                ef = self.robot.drive.front.readEncoders()
                eb = self.robot.drive.back.readEncoders()
                ea = ((ef[0]+eb[0])/2., (ef[1]+eb[1])/2.)
                if self.debug:
                    self.robot.logMsg("t(x+0.25): Encoder Front: 0=%d, 1=%d" % (ef[0],ef[1]))
                    self.robot.logMsg("t(x+0.25): Encoder Back: 0=%d, 1=%d" % (eb[0],eb[1]))
                    self.robot.logMsg("t(x+0.25): Encoder avg: 0=%3.2f 1=%3.2f" % (ea[0],ea[1]))

                
                ead = (abs(ea[0]-ea0[0]),abs(ea[1]-ea0[1]))
                if self.debug: # Debug instead of verbose, or at least low verbosity
                    self.robot.logMsg("t(x+0.25): ---> abs avg delta: %3.2f,  %3.2f" % (ead[0], ead[1]))
                if ead[0]>c or ead[1]>c:
                    if self.verbose:
                        self.robot.logMsg(" <<< t(stop): ---> abs avg delta: %3.2f,  %3.2f" % (ead[0], ead[1]))
                    if ead[0]>encoderError or ead[1]>encoderError:
                        self.robot.logMsg(" <<< WARNING: deltas too large to be believable; ignoring")
                    else:
                        self.robot.logMsg(" <<< Reached rotational count,  Stopping turn")
                        break
                # time.sleep(.25)
#                if n>10:
#                    self.robot.logMsg("Stopping after a count of 10")
#                    turning=False

            self.robot.drive.stop()
            if self.verbose:
                self.robot.logMsg("Stopped turning - Current turn target reached")
                
            time.sleep(2.5)
            # What's the slippage?
            ef = self.robot.drive.front.readEncoders()
            eb = self.robot.drive.back.readEncoders()
            ea = ((ef[0]+eb[0])/2., (ef[1]+eb[1])/2.)
            if self.debug:
                self.robot.logMsg("t(stop): Encoder Front: 0=%d, 1=%d" % (ef[0],ef[1]))
                self.robot.logMsg("t(stop): Encoder Back: 0=%d, 1=%d" % (eb[0],eb[1]))
                self.robot.logMsg("t(stop): Encoder avg: 0=%3.2f 1=%3.2f" % (ea[0],ea[1]))

                
            eadnow = (abs(ea[0]-ea0[0]),abs(ea[1]-ea0[1]))

            if self.verbose:
                self.robot.logMsg("t(stop): stopping delta: 0=%3.2f 1=%3.2f" % (ead[0],ead[1]))

                self.robot.logMsg("t(stop+5): current delta: 0=%3.2f 1=%3.2f" % (eadnow[0],eadnow[1]))

            
            lc+=1
            if lc>nr:
                self.robot.logMsg("Stopping - reached loop end : deltas: %2.1f , %2.1f" % (ead[0], ead[1]))
                break # looping=False


        self.robot.logMsg(" *** ACTION REQUIRED *****************************")
        self.robot.logMsg(" *** Please use front servo to measure error angle")
        time.sleep(5)
        self.robot.logMsg(" *** 10 sec left")
        time.sleep(5)
        self.robot.logMsg(" *** 5 sec left")
        time.sleep(5)
        self.robot.logMsg(" *** Time's up!")
        self.robot.logMsg(" *** ** *** *** *** *** *** *** *** *** *** *** ***")
        self.robot.logMsg(" Head angle: %d (degrees)" % int(round(self.robot.head.angle)))
        self.robot.logMsg(" *** ** *** *** *** *** *** *** *** *** *** *** ***")

        # robot.head.angle is in degrees, +tive == clockwise => have turned too much
        # (as we currently are turning ACW and overturning means need to move head to
        # right to compensate)
        # N.B. this assumes turning ACW, driveXY(-1,0) !!
        if int(round(self.robot.head.angle)):
               cfsign=-1 
               self.robot.turnCorrectionFactor=correctionfactor*((90+cfsign*(self.robot.head.angle/8))/90)
               self.robot.logMsg("Correction factor adjusted to %1.2f" % self.robot.turnCorrectionFactor)

               
    def straightFwdBack(self):
        elapsed = 0

        self.robot.logMsg("Starting to drive in a straight line:")
        ef0 = self.robot.drive.front.readEncoders()
        eb0 = self.robot.drive.back.readEncoders()
        self.robot.logMsg("t(0): Front encoders: %d , %d" % (ef0[0],ef0[1]))
        self.robot.logMsg("t(0): Rear encoders: %d , %d" % (eb0[0],eb0[1]))
        self.robot.drive.setDrive(1.0,0)
        delta=1
        time.sleep(delta)
        elapsed+=delta
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        efd = (ef[0]-ef0[0],ef[1]-ef0[1])
        ebd = (eb[0]-eb0[0],eb[1]-eb0[1])
        ef0 = ef
        eb0 = eb
        
        self.robot.logMsg("t(%2.1f): Front encoders delta: %d , %d" % (elapsed,efd[0],efd[1]))
        self.robot.logMsg("t(%2.1f): Rear encoders delta: %d , %d" % (elapsed,ebd[0],ebd[1]))

        self.robot.logMsg("Drive in straight line")
        self.robot.drive.setDrive(1.0,0)
        delta=4
        time.sleep(delta)
        elapsed+=delta
        
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        efd = (ef[0]-ef0[0],ef[1]-ef0[1])
        ebd = (eb[0]-eb0[0],eb[1]-eb0[1])
        ef0 = ef
        eb0 = eb
        self.robot.logMsg("t(%2.1f): Front encoders delta: %d , %d" % (elapsed,efd[0],efd[1]))
        self.robot.logMsg("t(%2.1f): Rear encoders delta: %d , %d" % (elapsed,ebd[0],ebd[1]))

        
        self.robot.logMsg("Start Reverse")
        self.robot.drive.setDrive(-1.0,0)

        delta=1
        time.sleep(delta)
        elapsed+=delta
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        efd = (ef[0]-ef0[0],ef[1]-ef0[1])
        ebd = (eb[0]-eb0[0],eb[1]-eb0[1])
        ef0 = ef
        eb0 = eb
        
        self.robot.logMsg("t(%2.1f): Front encoders delta: %d , %d" % (elapsed,efd[0],efd[1]))
        self.robot.logMsg("t(%2.1f): Rear encoders delta: %d , %d" % (elapsed,ebd[0],ebd[1]))

        
        self.robot.logMsg("And continue reversing")
        self.robot.drive.setDrive(-1.0,0)
        delta=4
        elapsed+=delta
        time.sleep(delta)
        
        ef = self.robot.drive.front.readEncoders()
        eb = self.robot.drive.back.readEncoders()
        efd = (ef[0]-ef0[0],ef[1]-ef0[1])
        ebd = (eb[0]-eb0[0],eb[1]-eb0[1])
        ef0 = ef
        eb0 = eb
        self.robot.logMsg("t(%2.1f): Front encoders delta: %d , %d" % (elapsed,efd[0],efd[1]))
        self.robot.logMsg("t(%2.1f): Rear encoders delta: %d , %d" % (elapsed,ebd[0],ebd[1]))

        
        self.robot.drive.stop()
        self.robot.logMsg("Stopping")


    def forwardBias(self,bias):
        self.robot.logMsg("Setting Bias Correction to %2.3f" % bias)
        self.robot.drive.setBiasCorrection(bias) # TTD also update local? ? 

        # Drive fwd for 5 sec
        self.robot.drive.setDriveXY(0,1)
        time.sleep(5)
        self.robot.drive.stop()
        
        self.robot.logMsg("Sleeping for 10 sec before continuing ... ")
        time.sleep(10)


        
    def run(self):
        self.robot.logMsg("Run Calibration module")
        # -0.0955
        ##currentBiasCorrection=-0.045 # It's going left; make it go right a bit
        ##currentBiasCorrectionDelta=0.025 # Keep making it go right
        # Now can be set by caller, or defaults above
#        currentBiasCorrection=-0.05 # It's going left; make it go right a bit
#        currentBiasCorrectionDelta=0.05 # Keep making it go right

        currentBiasCorrection=self.biasCorrection
        currentBiasCorrectionDelta=self.biasCorrectionDelta
        
        self.robot.logMsg("Setting Bias Correction to %2.3f" % currentBiasCorrection)
        self.robot.drive.setBiasCorrection(currentBiasCorrection)

        self.robot.drive.setSpeedFactor(3.0)
        # Ensure we are going forward, so the o/p makes sense
        self.robot.drive.setFlip(1)
        # TTD: also ensure head is at zero degrees
        self.robot.update()
        # TTD: check Drive and consider adding update to setFlip ?

        self.forwardBias(currentBiasCorrection)

        currentBiasCorrection+=currentBiasCorrectionDelta
        self.forwardBias(currentBiasCorrection)

        currentBiasCorrection+=currentBiasCorrectionDelta
        self.forwardBias(currentBiasCorrection)

        
#        currentBiasCorrection=0 #
        
        
        time.sleep(30)
        
        self.robot.drive.setBiasCorrection(0)
        self.straightFwdBack()
        time.sleep(10)
        
        self.turn()

        time.sleep(10)
        self.turn()
               
#        self.robot.logMsg("Sleeping for 20 before driving forward")
#        time.sleep(5)
#        self.robot.logMsg(" ... 15 sec left")
        self.robot.logMsg("Sleeping for 15 before driving forward")
        time.sleep(5)
        self.robot.logMsg(" ... 10 sec left")
        time.sleep(5)
        self.robot.logMsg(" ... 5 sec left")
        time.sleep(5)
        self.robot.logMsg(" ... Time's up!")

        self.straightFwdBack()

        # go backwards now to see how
        self.robot.logMsg(" Sleep for 10 sec before reversing")
        time.sleep(10)
        self.robot.drive.setFlip(0)
        self.straightFwdBack()
        
        self.robot.next_module(True)
        exit()


if __name__ == "__main__":
    from Camera import Camera
    camera = Camera()
    time.sleep(2)
    camera.stop()

