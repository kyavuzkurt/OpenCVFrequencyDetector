import cv2 as cv
import numpy as np
import csv
import time
import os
import datetime
from tqdm import tqdm

class ColorDetector:
    def __init__(self, video_paths, color, max_objects, amp, f, a, percentage):
        self.video_paths = video_paths
        self.color = color  
        self.max_objects = max_objects
        self.amp = amp
        self.f = f
        self.a = a
        self.percentage = percentage
        self.frame_count = 0
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

            total_frames = int(self.video.get(cv.CAP_PROP_FRAME_COUNT))
            for _ in tqdm(range(total_frames), desc="Processing frames"):
                ret, frame = self.video.read()
                if not ret:
                    print(f"End of video: {video_path}")  
                    break

                elapsed_time = time.time() - self.start_time
                fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0

                small_frame = cv.resize(frame, (640, 480))

                if self.frame_count % 1 == 0:  
                    # ArUco marker detection
                    gray = cv.cvtColor(small_frame, cv.COLOR_BGR2GRAY)
                    aruco_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
                    parameters = cv.aruco.DetectorParameters()
                    corners, ids, _ = cv.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

                    if ids is not None:
                        for i in range(len(ids)):
                            if i >= self.max_objects:
                                break
                            c = corners[i][0]
                            center = (int(c[:, 0].mean()), int(c[:, 1].mean()))
                            cv.aruco.drawDetectedMarkers(small_frame, corners)
                            writer.writerow([self.frame_count, ids[i][0], center[0], center[1]])

                cv.putText(small_frame, f"FPS: {fps:.2f}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv.LINE_AA)

                self.frame_count += 1
                cv.imshow('Frame', small_frame)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break

        self.video.release()
        cv.destroyAllWindows()