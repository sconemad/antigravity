import cv2
import threading
import time
import numpy as np

from picamera.array import PiRGBArray
from picamera import PiCamera


class Camera(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.cam = PiCamera(resolution=(640,480))
        self.cam.iso = 800

        # Crop the frame
        self.cam.zoom = (0.2, 0.2, 0.8, 0.8)

        # Allow time for the camera to "warm up"
        time.sleep(4.0)

        # Could try this to reduce incoming data:
        #self.cam.image_effect = "posterise"
        #self.cam.image_effect_params = 4
        # Turn off exposure compensation, set AWB to fluorescent for now
        self.cam.awb_mode = "fluorescent"
        self.cam.shutter_speed = self.cam.exposure_speed
        self.cam.exposure_mode = "off"
        gains = self.cam.awb_gains
        self.cam.awb_gains = gains
        self.ready = True
        self.daemon = True

    def adjust_gamma(self, gamma):
        # build a lookup table mapping the pixel values [0, 255] to their adjusted
        # gamma values
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
            # apply gamma correction using the lookup table
        return cv2.LUT(self.rawCapture.array, table)

    def find_colour(self, lower_range, upper_range, lower_split_range, upper_split_range):
        print("find a colour")
        height, width, cols = self.gamma_adjusted.shape
        #height, width, cols = self.rawCapture.array
        self.hsv = cv2.cvtColor(cv2.flip(self.gamma_adjusted, 0), cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(self.hsv, lower_range, upper_range)
        if lower_split_range is not np.empty:
            mask2 = cv2.inRange(self.hsv, lower_split_range, upper_split_range)
            mask = mask + mask2

        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        for cnt in contours:
            x,y,w,h = cv2.boundingRect(cnt)
            self.box_centre_x = x + (w / 2)
            self.box_centre_y = y + (h / 2)
            print(x,y,w,h, self.box_centre_x, self.box_centre_y)

            if self.box_centre_x >=((width / 2) - 100) and self.box_centre_x <=((width / 2) + 100):
                if (self.box_centre_y >= 0) and (self.box_centre_y <= 200):
                    print("Found Colour")
                    return True
        return False

    # def dominant_colour(self):
        # Z = image.reshape((-1,3))
        # Z = np.float32(Z)

        # print("Apply kmeans")
        # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        # K = 8
        # # Four iterations over the data - takes 3 seconds or so
        # ret,label,center=cv2.kmeans(Z, K, None, criteria, 4, cv2.KMEANS_RANDOM_CENTERS)

        # # Now convert back into uint8, and make original image
        # center = np.uint8(center)
        # res = center[label.flatten()]
        # res2 = res.reshape((image.shape))

        # _, counts = np.unique(label, return_counts=True)

        # counts.sort()
        # for i in range(0, len(counts)):
                # print("Cluster {0} count {1} is colour {2}".format(i, counts[i], center[i]))
        #
        # # Next - use cluster location for highest count which isn't low saturation or dark

    def stop(self):
        self.ready = False
        time.sleep(5)

    def run(self):
        while self.ready:
            self.rawCapture = PiRGBArray(self.cam)
            self.cam.capture(self.rawCapture, format="bgr")
            print("Capture frame");
            # Not sure how helpful the gamma adjustment is
            self.gamma_adjusted = self.adjust_gamma(1.5)
            #cv2.imshow("Frame",cv2.flip(self.gamma_adjusted, -1))
            #cv2.waitKey(2)

if __name__ == "__main__":
    camera = Camera()
    camera.run()
