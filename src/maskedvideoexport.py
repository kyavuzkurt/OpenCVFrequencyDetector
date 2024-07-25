import cv2 as cv
import os
import datetime
import argparse
import numpy as np
from tqdm import tqdm

timestamp = datetime.datetime.now()

parser = argparse.ArgumentParser(description='Masked Video Export')
parser.add_argument('--video_path', type=str, required=True, help='Path to the video file')
parser.add_argument('--color_number', type=int, required=True, help='Color number (1 for green, 2 for blue)')
parser.add_argument('--amp', type=float, required=True, help='Amplitude value')
parser.add_argument('--f', type=float, required=True, help='Frequency value')
parser.add_argument('--p', type=float, required=True, help='Percentage value')
parser.add_argument('--a', type=float, required=True, help='Variable a value')

args = parser.parse_args()

if args.color_number == 1:
    hue_low, saturation_low, value_low = 25, 60, 60
    hue_high, saturation_high, value_high = 95, 255, 255
elif args.color_number == 2:
    hue_low, saturation_low, value_low = 100, 150, 50
    hue_high, saturation_high, value_high = 140, 255, 255

video_path = args.video_path
masked_video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "masked_videos")
bounding_video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bounding_videos")
os.makedirs(masked_video_dir, exist_ok=True)
os.makedirs(bounding_video_dir, exist_ok=True)

video = cv.VideoCapture(video_path)
if not video.isOpened():
    print(f"Error: Could not open video file {video_path}")
    exit(1)

total_frames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
frame_width = 1280
frame_height = 720

bounding_box_path = os.path.join(bounding_video_dir, f"camera_bounding_box_{args.color_number}_amp_{args.amp}_f_{args.f}_p_{args.p}_a_{args.a}_{timestamp}.mp4")
masked_video_path = os.path.join(masked_video_dir, f"camera_masked_{args.color_number}_amp_{args.amp}_f_{args.f}_p_{args.p}_a_{args.a}_{timestamp}.mp4")
fourcc = cv.VideoWriter_fourcc(*'mp4v')

# Initialize the VideoWriter with the correct frame size
out_masked = cv.VideoWriter(masked_video_path, fourcc, 30, (frame_width, frame_height))
out_bounding= cv.VideoWriter(bounding_box_path, fourcc, 30, (frame_width, frame_height))

# Initialize the progress bar
with tqdm(total=total_frames, desc="Processing Video") as pbar:
    while True:
        ret, frame = video.read()
        if not ret or frame is None:
            break
        
        frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lowerBound = np.array([hue_low, saturation_low, value_low])
        upperBound = np.array([hue_high, saturation_high, value_high])
        mask = cv.inRange(frameHSV, lowerBound, upperBound)

        kernel = np.ones((3, 3), np.uint8)
        mask = cv.erode(mask, kernel, iterations=2)
        mask = cv.dilate(mask, kernel, iterations=2)
        masked_frame = cv.bitwise_and(frame, frame, mask=mask)
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        multi_tracker = cv.legacy.MultiTracker_create()

        for c in contours:
            area = cv.contourArea(c)
            if area > 5:
                x, y, w, h = cv.boundingRect(c)
                tracker = cv.legacy.TrackerKCF_create()
                multi_tracker.add(tracker, frame, (x, y, w, h))

        success, boxes = multi_tracker.update(frame)
        out_bounding.write(frame)
        out_masked.write(masked_frame)
        
        pbar.update(1)

out_masked.release()
out_bounding.release()
video.release()
print(f"Masked video exported successfully to {masked_video_path}.")
print(f"Bounding video exported successfully to {bounding_box_path}.")
cv.destroyAllWindows()