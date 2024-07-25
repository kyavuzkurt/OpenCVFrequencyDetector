import cv2 as cv
import numpy as np
import csv
import time
import os
import datetime

class ColorDetector:
    def __init__(self, video_paths, color, max_objects, amp, f, a, percentage):
        self.video_paths = video_paths
        self.color = color  
        self.max_objects = max_objects
        self.amp = amp
        self.f = f
        self.a = a
        self.percentage = percentage
        if color == 'green':
            self.hue_low, self.saturation_low, self.value_low = 25, 60, 60
            self.hue_high, self.saturation_high, self.value_high = 95, 255, 255
        elif color == 'blue':
            self.hue_low, self.saturation_low, self.value_low = 100, 150, 50
            self.hue_high, self.saturation_high, self.value_high = 140, 255, 255
        self.frame_count = 0
        self.multi_tracker = cv.legacy.MultiTracker_create()
        self.start_time = time.time()

    def run(self, video_path, video_index):
        self.frame_count = 0  
        print(f"Processing video: {video_path}")  
        self.video = cv.VideoCapture(video_path)
        if not self.video.isOpened():
            print(f"Error: Could not open video. Path: {video_path}")
            return

        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../output_csvs")
        os.makedirs(output_dir, exist_ok=True)

        color_number = '1' if self.color == 'green' else '2'
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
        
        output_file = os.path.join(output_dir, f"camera_{color_number}_amp_{self.amp}_f_{self.f}_p_{self.percentage}_a_{self.a}_{timestamp}.csv")

        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frame', 'ID', 'X', 'Y'])

            while True:
                ret, frame = self.video.read()
                if not ret:
                    print(f"End of video: {video_path}")  # Informative message instead of an error
                    break

                # Calculate FPS
                elapsed_time = time.time() - self.start_time
                fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0

                # Resize frame to 720p
                frame = cv.resize(frame, (1280, 720))

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
                        if area > 5:
                            x, y, w, h = cv.boundingRect(c)
                            tracker = cv.legacy.TrackerKCF_create()
                            self.multi_tracker.add(tracker, frame, (x, y, w, h))
                            tracked_objects += 1

                success, boxes = self.multi_tracker.update(frame)
                frame_height = frame.shape[0]
                frame_width = frame.shape[1]

                if self.color == 'blue':
                    x_min = int(0.3516 * frame_width)
                    x_max = int(0.5313 * frame_width)
                    y_min = int(0.2361 * frame_height)
                    y_max = int(0.6944 * frame_height)
                else:
                    x_min = int(0)
                    x_max = int(frame_width)
                    y_min = int(0.2 * frame_height)
                    y_max = int(0.8 * frame_height)

                for i, box in enumerate(boxes):
                    x, y, w, h = [int(v) for v in box]
                    center = (x + w // 2, y + h // 2)

                    if x_min <= center[0] <= x_max and y_min <= center[1] <= y_max:
                        rect_color = (0, 255, 0) if self.color == 'blue' else (255, 0, 0)
                        cv.rectangle(frame, (x, y), (x + w, y + h), rect_color, 2)
                        cv.circle(frame, center, 5, (0, 255, 0), -1)
                        writer.writerow([self.frame_count, i + 1, center[0], center[1]])

                cv.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv.LINE_AA)

                frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
                mask = cv.inRange(frameHSV, lowerBound, upperBound)
                masked_frame = cv.bitwise_and(frame, frame, mask=mask)
                

                self.frame_count += 1
                cv.imshow("Tracking", frame)
                cv.imshow("Masked", masked_frame)
                if cv.waitKey(1) == ord('q'):
                    break
        self.video.release()
        cv.destroyAllWindows()