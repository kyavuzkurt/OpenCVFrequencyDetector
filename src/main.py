import colordetector as cd
import cv2 as cv
import csv
import datetime
import argparse
import logging
import os

logging.basicConfig(level=logging.DEBUG)

def main():
    parser = argparse.ArgumentParser(description='Color Detector with MultiTracker')
    parser.add_argument('--video', '-v', type=str, help='Path to the video file', required=True)
    parser.add_argument('--color', '-c', type=str, choices=['blue', 'green'], help='Color to detect', required=True)
    parser.add_argument('--max_objects', '-m', type=int, default=12, help='Maximum number of objects to track')
    args = parser.parse_args()

    video_path = os.path.abspath(args.video)
    logging.debug(f"Absolute path to video: {video_path}")

    if not os.path.exists(video_path):
        logging.error(f"Video file does not exist: {video_path}")
        return

    detector = cd.ColorDetector([video_path], args.color, args.max_objects)
    detector.run(video_path, 0)

if __name__ == "__main__":
    main()