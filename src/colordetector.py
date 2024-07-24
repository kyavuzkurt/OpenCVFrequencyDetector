import cv2 as cv
import numpy as np
import csv
import time
import os
import datetime



class ColorDetector:
    def __init__(self, video_paths, color, max_objects=12):
        self.video_paths = video_paths
        self.max_objects = max_objects
        if color == 'green':
            self.hue_low, self.saturation_low, self.value_low = 25, 80, 80
            self.hue_high, self.saturation_high, self.value_high = 95, 255, 255
        elif color == 'blue':
            self.hue_low, self.saturation_low, self.value_low = 110, 50, 50
            self.hue_high, self.saturation_high, self.value_high = 130, 255, 255
        self.frame_count = 0
        self.multi_tracker = cv.legacy.MultiTracker_create()

    def run(self, video_path, video_index):
        self.frame_count = 0  
        print(f"Processing video: {video_path}")  
        self.video = cv.VideoCapture(video_path)
        if not self.video.isOpened():
            print(f"Error: Could not open video. Path: {video_path}")
            return

        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../output_csvs")
        os.makedirs(output_dir, exist_ok=True)

        now = datetime.datetime.now()
        output_file = os.path.join(output_dir, now.strftime("%Y-%m-%d_%H-%M-%S") + ".csv")

       
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter('masked_video.mp4', fourcc, 20.0, (int(self.video.get(3)), int(self.video.get(4))))

        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frame', 'ID', 'X', 'Y'])

            while True:
                ret, frame = self.video.read()
                if not ret:
                    print(f"Error: Could not read frame from {video_path}") 
                    break

                if self.frame_count % 1 == 0:  
                    self.multi_tracker = cv.legacy.MultiTracker_create()
                    frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
                    lowerBound = np.array([self.hue_low, self.saturation_low, self.value_low])
                    upperBound = np.array([self.hue_high, self.saturation_high, self.value_high])
                    mask = cv.inRange(frameHSV, lowerBound, upperBound)

                    kernel = np.ones((3, 3), np.uint8)
                    mask = cv.erode(mask, kernel, iterations=2)
                    mask = cv.dilate(mask, kernel, iterations=2)

                    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                    tracked_objects = 0
                    for c in contours:
                        if tracked_objects >= self.max_objects:
                            break
                        area = cv.contourArea(c)
                        if area > 20:
                            x, y, w, h = cv.boundingRect(c)
                            tracker = cv.legacy.TrackerKCF_create()
                            self.multi_tracker.add(tracker, frame, (x, y, w, h))
                            tracked_objects += 1

                success, boxes = self.multi_tracker.update(frame)
                frame_height = frame.shape[0]
                y_min = int(0.2 * frame_height)
                y_max = int(0.8 * frame_height) #optional parameters for ROI

                for i, box in enumerate(boxes):
                    x, y, w, h = [int(v) for v in box]
                    center = (x + w // 2, y + h // 2)

                    if y_min <= center[1] <= y_max:
                        cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        cv.circle(frame, center, 5, (0, 255, 0), -1)
                        writer.writerow([self.frame_count, i + 1, center[0], center[1]])

                frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
                mask = cv.inRange(frameHSV, lowerBound, upperBound)
                masked_frame = cv.bitwise_and(frame, frame, mask=mask)
                out.write(masked_frame)  

                self.frame_count += 1
                cv.imshow("Tracking", frame)
                cv.imshow("Masked", masked_frame)
                if cv.waitKey(1) == ord('q'):
                    break

        self.video.release()
        out.release()  
        cv.destroyAllWindows()