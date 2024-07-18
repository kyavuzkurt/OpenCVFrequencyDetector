import cv2 as cv
import numpy as np
import csv  # Import csv module
import time

# Remove the problematic import
# from main import hue_low, saturation_low, value_low, hue_high, saturation_high, value_high

# Define the HSV ranges directly in colordetector.py
hue_low = 25
saturation_low = 50
value_low = 50
hue_high = 95
saturation_high = 255
value_high = 255

class ColorDetector:
    def __init__(self, video_paths):
        self.video_paths = video_paths
        self.hue_low, self.saturation_low, self.value_low = hue_low, saturation_low, value_low  # Use defined values
        self.hue_high, self.saturation_high, self.value_high = hue_high, saturation_high, value_high  # Use defined values
        self.frame_count = 0

        self.setup_trackbars()

    def setup_trackbars(self):
        cv.namedWindow('HSV sliders')
        cv.moveWindow('HSV sliders', 50, 50)

        cv.createTrackbar('Hue Low', 'HSV sliders', self.hue_low, 179, self.onTracker1)  # Use initial values
        cv.createTrackbar('Saturation Low', 'HSV sliders', self.saturation_low, 255, self.onTracker2)  # Use initial values
        cv.createTrackbar('Value Low', 'HSV sliders', self.value_low, 255, self.onTracker3)  # Use initial values
        cv.createTrackbar('Hue High', 'HSV sliders', self.hue_high, 179, self.onTracker4)  # Use initial values
        cv.createTrackbar('Saturation High', 'HSV sliders', self.saturation_high, 255, self.onTracker5)  # Use initial values
        cv.createTrackbar('Value High', 'HSV sliders', self.value_high, 255, self.onTracker6)  # Use initial values

    def onTracker1(self, val):
        self.hue_low = val
        print("Hue Low", self.hue_low)

    def onTracker2(self, val):
        self.saturation_low = val
        print("Saturation Low", self.saturation_low)

    def onTracker3(self, val):
        self.value_low = val
        print("Value Low", self.value_low)

    def onTracker4(self, val):
        self.hue_high = val
        print("Hue High", self.hue_high)

    def onTracker5(self, val):
        self.saturation_high = val
        print("Saturation High", self.saturation_high)

    def onTracker6(self, val):
        self.value_high = val
        print("Value High", self.value_high)

    def run(self, video_path, video_index):
        self.frame_count = 0  # Reset frame count for each video
        print(f"Processing video: {video_path}")  # Debugging statement
        self.video = cv.VideoCapture(video_path)
        if not self.video.isOpened():
            print(f"Error: Could not open video. Path: {video_path}")
            return

        with open(f'output_{video_index}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frame', f'X{video_index}', f'Y{video_index}', f'Width{video_index}', f'Height{video_index}'])
            while True:
                ret, frame = self.video.read()
                if not ret:
                    print(f"Error: Could not read frame from {video_path}")  # Debugging statement
                    break
                frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
                lowerBound = np.array([self.hue_low, self.saturation_low, self.value_low])
                upperBound = np.array([self.hue_high, self.saturation_high, self.value_high])
                mask = cv.inRange(frameHSV, lowerBound, upperBound)

                # Apply morphological operations to reduce noise
                kernel = np.ones((3, 3), np.uint8)
                mask = cv.erode(mask, kernel, iterations=2)
                mask = cv.dilate(mask, kernel, iterations=2)

                contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                for c in contours:
                    area = cv.contourArea(c)
                    if area > 100:
                        x, y, w, h = cv.boundingRect(c)
                        cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)
                        writer.writerow([self.frame_count, x, y, w, h])
                self.frame_count += 1
                cv.imshow("Camera", frame)
                myObject = cv.bitwise_and(frame, frame, mask=mask)
                smallMask = cv.resize(mask, (int(frame.shape[1] / 2), int(frame.shape[0] / 2)))
                cv.imshow("Small Mask", smallMask)
                smallObject = cv.resize(myObject, (int(frame.shape[1] / 2), int(frame.shape[0] / 2)))
                cv.imshow("Small Object", smallObject)
                if cv.waitKey(1) == ord('q'):
                    break
        self.video.release()
        cv.destroyAllWindows()