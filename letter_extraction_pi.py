from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np 
import cv2
import matplotlib
matplotlib.use('PS')
from matplotlib import pyplot as plt
from scipy import ndimage

from model.serve import load_model, predict

# bunch of values we can vary
surfHessian = 500
width = 640
height = 480

def main():
    
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (width, height)
    camera.framerate = 16
    rawCapture = PiRGBArray(camera, size=(width, height))
    
    # allow the camera to warmup
    time.sleep(0.1)
    
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
    
        # image processing
        crop_img = image[(int)(height/2-30):(int)(height/2+30), (int)(width/2-18):(int)(width/2+18)]
        crop_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        # equi_gray = cv2.equalizeHist(crop_gray)
        clipLimit = 10.0
        tileGridSize = (4,4)
        clahe = cv2.createCLAHE(clipLimit, tileGridSize)
        equi_gray = clahe.apply(crop_gray)
        kernel = np.ones((7,7),np.uint8)
        opening_gray = cv2.morphologyEx(equi_gray, cv2.MORPH_OPEN, kernel)
        invert_img = cv2.bitwise_not(opening_gray)

        h, w = invert_img.shape
        for i in range(h):
            for j in range(w):
                if invert_img.item(i,j) < 150:
                    invert_img.itemset((i,j),0)
        
        # show cropped frame
        cv2.rectangle(frame,(width//2-18,height//2-30),(width//2+18,height//2+30),(0,0,255),3,-1)
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF
        cv2.imshow('invert_img', invert_img)

        # make letter prediction
        print(predict(invert_img, model, mapping))
    
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
    
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

if __name__=="__main__":
    main()