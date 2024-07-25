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
os.makedirs(masked_video_dir, exist_ok=True)

video = cv.VideoCapture(video_path)
if not video.isOpened():
    print(f"Error: Could not open video file {video_path}")
    exit(1)

total_frames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
frame_width = 1280
frame_height = 720

masked_video_path = os.path.join(masked_video_dir, f"camera_masked_{args.color_number}_amp_{args.amp}_f_{args.f}_p_{args.p}_a_{args.a}_{timestamp}.mp4")
fourcc = cv.VideoWriter_fourcc(*'mp4v')

out_masked = cv.VideoWriter(masked_video_path, fourcc, 30, (frame_width, frame_height))

lowerBound = np.array([hue_low, saturation_low, value_low])
upperBound = np.array([hue_high, saturation_high, value_high])
kernel = np.ones((3, 3), np.uint8)

with tqdm(total=total_frames, desc="Processing Video") as pbar:
    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        frameHSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        mask = cv.inRange(frameHSV, lowerBound, upperBound)
        mask = cv.erode(mask, kernel, iterations=2)
        mask = cv.dilate(mask, kernel, iterations=2)
        masked_frame = cv.bitwise_and(frame, frame, mask=mask)
        out_masked.write(masked_frame)
        
        pbar.update(1)

out_masked.release()
video.release()
print(f"Masked video exported successfully to {masked_video_path}.")
cv.destroyAllWindows()