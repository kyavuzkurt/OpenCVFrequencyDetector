import cv2 as cv
import numpy as np
import csv
import time
import os
import datetime
from tqdm import tqdm

class ColorDetector:
    def __init__(self, video_path, max_objects, color_code, preview_enabled, progress_bar=None):
        self.video_path = video_path
        self.max_objects = max_objects
        self.frame_count = 0
        self.start_time = time.time()
        self.first_frame = None
        self.color_code = color_code
        self.preview_enabled = preview_enabled
        self.hue_low = int(color_code[:3])
        self.hue_high = int(color_code[3:6])
        self.saturation_low = int(color_code[6:9])
        self.saturation_high = int(color_code[9:12])
        self.value_low = int(color_code[12:15])
        self.value_high = int(color_code[15:18])
        self.progress_bar = progress_bar

    def run(self):
        self.frame_count = 0  
        print(f"Processing video: {self.video_path}")  
        self.video = cv.VideoCapture(self.video_path)
        if not self.video.isOpened():
            print(f"Error: Could not open video. Path: {self.video_path}")
            return

        self.first_frame = self.video.read()[1]
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../output_csvs")
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
        
        output_file = os.path.join(output_dir, f"cc_{self.color_code}_obj_{self.max_objects}_{timestamp}.csv")
        
        frame_width = int(self.video.get(cv.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.video.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = self.video.get(cv.CAP_PROP_FPS)
    
        if not self.preview_enabled:
            fourcc = cv.VideoWriter_fourcc(*'mp4v')
            masked_output = cv.VideoWriter(os.path.join(output_dir, f"masked_output_{timestamp}.mp4"), fourcc, fps, (frame_width, frame_height), isColor=False)
            tracked_output = cv.VideoWriter(os.path.join(output_dir, f"tracked_output_{timestamp}.mp4"), fourcc, fps, (frame_width, frame_height))

        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frame', 'ID', 'X', 'Y'])

            total_frames = int(self.video.get(cv.CAP_PROP_FRAME_COUNT))
            for frame_idx in tqdm(range(total_frames), desc="Processing frames"):
                ret, frame = self.video.read()
                if not ret:
                    print(f"End of video: {self.video_path}")  
                    break

                elapsed_time = time.time() - self.start_time
                fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0

                frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
                lowerBound = np.array([self.hue_low, self.saturation_low, self.value_low])
                upperBound = np.array([self.hue_high, self.saturation_high, self.value_high])
                mask = cv.inRange(frameHSV, lowerBound, upperBound)

                kernel = np.ones((3, 3), np.uint8)
                mask = cv.erode(mask, kernel, iterations=2)
                mask = cv.dilate(mask, kernel, iterations=2)

                contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

                tracked_frame = frame.copy()
                tracked_objects = 0
                for c in contours:
                    area = cv.contourArea(c)
                    if area > 1:
                        x, y, w, h = cv.boundingRect(c)
                        center_x = x + w // 2
                        center_y = y + h // 2

                        if x <= center_x <= x + w and y <= center_y <= y + h:
                            tracked_objects += 1
                            rect_color = (255, 0, 0)
                            
                            cv.rectangle(tracked_frame, (x, y), (x + w, y + h), rect_color, 2)
                            cv.drawMarker(tracked_frame, (center_x, center_y), rect_color, cv.MARKER_CROSS, 10, 2)
                            label = f"ID: {tracked_objects}"
                            cv.putText(tracked_frame, label, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, rect_color, 2)

                            writer.writerow([self.frame_count, tracked_objects, center_x, center_y])

                            if tracked_objects >= self.max_objects:
                                break

                cv.putText(tracked_frame, f"FPS: {fps:.2f}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv.LINE_AA)

                self.frame_count += 1

                if not self.preview_enabled:
                    masked_output.write(mask)
                    tracked_output.write(tracked_frame)
                elif self.preview_enabled:
                    resized_tracked_frame = cv.resize(tracked_frame, (640, 480))
                    resized_mask = cv.resize(mask, (640, 480))
                    cv.imshow('Tracked Frame', resized_tracked_frame)
                    cv.imshow('Mask', resized_mask)
                    if cv.waitKey(1) & 0xFF == ord('q'):
                        break

                if self.progress_bar:
                    self.progress_bar['value'] = frame_idx + 1

        self.video.release()
        if not self.preview_enabled:
            masked_output.release()
            tracked_output.release()
        cv.destroyAllWindows()

def get_total_frames(video_path):
    video = cv.VideoCapture(video_path)
    total_frames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
    video.release()
    return total_frames

