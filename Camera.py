import cv2
import threading
import time
import numpy as np


class Camera(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.capture = cv2.VideoCapture(0)
        print(self.capture)
        self.running = True
        self.daemon = True
        self.start()
        time.sleep(2)

    def adjust_gamma(self,gamma):
        # build a lookup table mapping the pixel values [0, 255] to their adjusted
        # gamma values
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
            # apply gamma correction using the lookup table
        return cv2.LUT(self.frame, table)


    def find_colour(self,lower_range,upper_range):
        if self.result:
            height,width,cols = self.frame_gamma.shape
            self.hsv = cv2.cvtColor(cv2.flip(self.frame_gamma,0),cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(self.hsv,lower_range,upper_range)
            #cv2.imshow("mask",mask)
            #cv2.waitKey(1)
            contours = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                self.box_centre_x = x+(w / 2)
                self.box_centre_y = y+(h / 2)
                print(x,y,w,h, self.box_centre_x, self.box_centre_y)

                if self.box_centre_x >=((width / 2)-100) and self.box_centre_x <=((width / 2)+100):

                    if (self.box_centre_y >= 0) and (self.box_centre_y <= 200):
                        #cv2.rectangle(self.frame,(x,y),(x+w,y+h),(0,0,0),2)
                        print("Found Colour")
                        return True
            return False

    def stop(self):
        self.running = False
        time.sleep(5)

    def run(self):
        while self.running:
            self.result, self.frame = self.capture.read()
            #print(self.result)
            if self.result:
                self.frame_gamma = self.adjust_gamma(2.5)
                height,width,cols = self.frame.shape
                cv2.rectangle(self.frame_gamma,((width/2)-50,height),((width/2)+50,(height-200)),(0,0,0),3)
                #cv2.imshow("Frame",cv2.flip(self.frame_gamma,-1))
                #cv2.waitKey(2)



if __name__ == "__main__":
        camera = Camera()
