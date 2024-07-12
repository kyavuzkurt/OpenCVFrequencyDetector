import cv2 as cv
import argparse
import numpy as np
import csv  # Import csv module

parser = argparse.ArgumentParser(description='Color Detector')
parser.add_argument('--video', '-v', type=str, help='Path to the video file', default=0)
args = parser.parse_args()

video_path = args.video

# Initialize global variables for trackbars
hue_low, saturation_low, value_low = 10, 100, 100
hue_high, saturation_high, value_high = 30, 255, 255

def onTracker1(val):
    global hue_low
    hue_low = val
    print("Hue Low", hue_low)

def onTracker2(val):
    global saturation_low
    saturation_low = val
    print("Saturation Low", saturation_low)

def onTracker3(val):
    global value_low
    value_low = val
    print("Value Low", value_low)

def onTracker4(val):
    global hue_high
    hue_high = val
    print("Hue High", hue_high)

def onTracker5(val):
    global saturation_high
    saturation_high = val
    print("Saturation High", saturation_high)

def onTracker6(val):
    global value_high
    value_high = val
    print("Value High", value_high)

video = cv.VideoCapture(video_path)


if not video.isOpened():
    print(f"Error: Could not open video. Path: {video_path}")
    exit()

cv.namedWindow('HSV sliders')
cv.moveWindow('HSV sliders', 50, 50)

cv.createTrackbar('Hue Low', 'HSV sliders', 10, 179, onTracker1)
cv.createTrackbar('Saturation Low', 'HSV sliders', 100, 255, onTracker2)
cv.createTrackbar('Value Low', 'HSV sliders', 100, 255, onTracker3)
cv.createTrackbar('Hue High', 'HSV sliders', 30, 179, onTracker4)
cv.createTrackbar('Saturation High', 'HSV sliders', 255, 255, onTracker5)
cv.createTrackbar('Value High', 'HSV sliders', 255, 255, onTracker6)

with open('output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
  
    writer.writerow(['Frame', 'X', 'Y', 'Width', 'Height'])

    frame_count = 0  

    while True:
        ret, frame = video.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        frameHSV=cv.cvtColor(frame,cv.COLOR_BGR2HSV)
        loverBound = np.array([hue_low, saturation_low, value_low])
        upperBound = np.array([hue_high, saturation_high, value_high])
        mask=cv.inRange(frameHSV,loverBound,upperBound)
        contours, junk = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv.contourArea(c)
            if area > 100:
                x,y,w,h = cv.boundingRect(c)
                cv.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),3)
                
                writer.writerow([frame_count, x, y, w, h])
        frame_count += 1  
        cv.imshow("Camera", frame)
        #cv.imshow("Mask",mask)
        myObject = cv.bitwise_and(frame, frame, mask=mask)
        smallMask = cv.resize(mask,(int(frame.shape[1]/2), int(frame.shape[0]/2)))
        cv.imshow("Small Mask",smallMask)
        smallObject = cv.resize(myObject,(int(frame.shape[1]/2), int(frame.shape[0]/2)))
        cv.imshow("Small Object",smallObject)
        if cv.waitKey(1) == ord('q'):
            break
video.release()
cv.destroyAllWindows()