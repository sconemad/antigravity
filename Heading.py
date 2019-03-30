#
# 
# Using request-response not pub-sub
#
import os
from Module import Module
import sys
import zmq
import time


class Heading(Module):

    def __init__(self, bot):
        Module.__init__(self, bot, "Heading")
        #  Socket to talk to server
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.InitialHeading = 0.00
        self.Calibrating_p = False
        self.Calibrated_p = False

        #socket.connect("tcp://localhost:5556")
        try:
            self.socket.connect("ipc:////tmp/0mq_rr.ipc")
            self.logMsg("Heading Module: Connected to Gyro server socket")
        except:
            self.logMsg("ERROR - Heading Module: Connection to Gyro server socket FAILED")

        
    def start(self):
    #def start(self,bot):
        #self.bot = bot
        #cmd = os.popen("/home/pi/bin/getWlanIP.sh")
        #ip = cmd.readlines()
        #self.WLAN_IP_ADDR = ip[0].strip()
        self.logMsg("Heading: Starting calibration")
        self.getInitialHeading()
        
    def getInitialHeading(self):
        # Assumes heading is 0 -> 360 
        if self.Calibrating_p is True:
            print("  Warning: Calibration currently in progress.  Skipping calibration")
            return 0.00
        else:
            self.Calibrating_p = True
            print("  CALIBRATING - READING CURRENT HEADING  ");

            IH = []
            count = 30
            while ( count > 0 ):
                InitialHeading = self.getHeading()
                print(" Reading heading count %d  %3.2f" % (count,InitialHeading))
                IH.append(InitialHeading)
                time.sleep(0.05)
                count -= 1
            InitialHeading = 0
            RunningAvg = 0
            count = 0
            for i in IH:
                InitialHeading += i
                # Handle things close to 0 / 360 switchover so it doesn't mess up the average
                i -= 180
                delta = RunningAvg - i
                if delta > 180:
                    i += 360
                if delta < 180:
                    i -= 360
                RunningAvg = ( RunningAvg * count + i)/(count + 1)    
                    

            RunningAvg += 180
            if RunningAvg < 0:
                RunningAvg += 360
                
            InitialHeading = InitialHeading / len(IH)
            print("Average InitialHeading: %3.2f / %3.2f    " % ( InitialHeading, RunningAvg)  )
            self.InitialHeading = RunningAvg
            self.Calibrated_p = True
            self.Calibrating_p = False
            return InitialHeading


        
    def __del__(self):
        # Close sockets cleanly
        return 0

    def getHeading(self):
        self.socket.send(b"Hello")
        
        #  Get the reply.
        string = self.socket.recv_string()
    

        # print("GOT: %s" % string)
        # typestr, kalmanXs, kalmanYs, sepstr, rateXs, rateYs, sepstr2, timestampstr = string.split()  # @@@ TTD FIX MESSAGE FORMAT @@@
        typestr, kalmanXs, kalmanYs, kalmanZs, sepstr0, headingZs, sepstr, rateXs, rateYs, sepstr2, timestampstr = string.split()
        
        kalmanX = float(kalmanXs)
        kalmanY = float(kalmanYs)
        kalmanZ = float(kalmanZs)
        heading = float(headingZs)

        # rateX = float(rateXs)
        # rateX = round(float(rateXs) - gyroRateOffsetX)
        # rateX = round((float(rateXs)  + rateX3 + rateX2)/4  - gyroRateOffsetX)
        rateX = float(rateXs)
    
        rateY = float(rateYs)
        state = [kalmanX, kalmanY, kalmanZ, heading, rateX, rateY]
        return heading

    
    def getStatus(self):
        # print("Heading: Sending request  ...")
        # self.socket.send(b"Hello")
        # Note: if the server dies, then the display hangs waiting here ..
        # print("Heading: Sent.  Waiting for reply")
        #  Get the reply.
        # message = self.socket.recv_string()
        #print("Heading: Received reply [ %s ]" %  message)
        # [ KALMAN 15.48 -1.02 36.30 HEADING 22.0 GYRORATE -0.1  0.3 TIMESTAMP 1553959058465 ]

        # Avoid running heading if calibrating, else socket collision possible, 
        if self.Calibrated_p is True:
            InitialHeadingStr = "@%3.1f" % self.InitialHeading
        else:
            InitialHeadingStr = "@---"
        if self.Calibrating_p is True:
            headingStr = "CAL."
        else:
            headingStr = "%2.1f" % self.getHeading()
            
        heading = headingStr + "   " +   InitialHeadingStr 
        return heading
