import colordetector as cd
import cv2 as cv
import csv
import datetime
import argparse
import subprocess
import concurrent.futures
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)

class VideoCropper:
    def __init__(self, video_path):
        self.video_path = video_path
        logging.debug(f"Initializing VideoCropper with video path: {video_path}")
        self.crop_regions = self._calculate_crop_regions()

    def _calculate_crop_regions(self):
        logging.debug("Calculating crop regions")
        cap = cv.VideoCapture(self.video_path)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise ValueError("Could not read the first frame of the video")

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # Define the further adjusted green color range in HSV
        lower_green_final = np.array([25, 50, 50])
        upper_green_final = np.array([95, 255, 255])

        # Create a mask for the green color
        mask_final = cv.inRange(hsv, lower_green_final, upper_green_final)

        # Apply morphological operations to reduce noise
        kernel = np.ones((3, 3), np.uint8)
        mask_final = cv.erode(mask_final, kernel, iterations=2)
        mask_final = cv.dilate(mask_final, kernel, iterations=2)

        cv.imwrite('mask_final.png', mask_final)  # Save the mask for debugging

        contours, _ = cv.findContours(mask_final, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        crop_regions = []
        for cnt in contours:
            x, y, w, h = cv.boundingRect(cnt)
            crop_regions.append((x, y, w, h))

        crop_regions = sorted(crop_regions, key=lambda region: region[2] * region[3], reverse=True)[:12]
        crop_regions.sort(key=lambda region: region[0])

        logging.debug(f"Crop regions calculated: {crop_regions}")
        return crop_regions

    def get_cropped_videos(self):
        video_paths = []

        def crop_video(region, i):
            output_path = f"cropped_video_{i}.mp4"
            x, y, w, _ = region  

            tolerance = 10
            x = max(0, x - tolerance)
            w += 2 * tolerance

            cap = cv.VideoCapture(self.video_path)
            frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            if x + w > frame_width:
                w = frame_width - x

            if w <= 0:
                raise ValueError(f"Invalid crop dimensions for region {i}: width={w}")

            command = [
                'ffmpeg', '-i', self.video_path, '-vf',
                f"crop={w}:{frame_height}:{x}:0",  
                '-c:a', 'copy', output_path
            ]
            logging.debug(f"Running command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                logging.error(f"Error cropping video {i}: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, command)
            logging.debug(f"Cropped video saved to: {output_path}")
            return output_path

        with concurrent.futures.ThreadPoolExecutor() as executor:
            video_paths = list(executor.map(lambda i: crop_video(self.crop_regions[i], i), range(len(self.crop_regions))))

        logging.debug(f"Cropped videos: {video_paths}")
        return video_paths


class FrequencyDetector:

    def get_frequency_data(self, video_paths):
        for i, video_path in enumerate(video_paths):
            logging.debug(f"Processing video: {video_path}")
            color_detector = cd.ColorDetector([video_path])
            color_detector.run(video_path, i)  
            frame_count = color_detector.video.get(cv.CAP_PROP_FRAME_COUNT)
            logging.debug(f"Video: {video_path}, Frame Count: {frame_count}")
            color_detector.video.release()

def main():
    parser = argparse.ArgumentParser(description='Frequency Detector')
    parser.add_argument('--video', '-v', type=str, help='Path to the video file', required=True)
    args = parser.parse_args()

    video_path = args.video
    logging.debug(f"Video path provided: {video_path}")
    cropper = VideoCropper(video_path)
    cropped_videos = cropper.get_cropped_videos()

    frequency_detector = FrequencyDetector()
    frequency_detector.get_frequency_data(cropped_videos)

    now = datetime.datetime.now()
    output_file = now.strftime("%d-%m-%Y_%H:%M:%S") + ".csv"
    logging.debug(f"Output file: {output_file}")

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Frame', 'X', 'Y', 'Width', 'Height'])

        for i, video_path in enumerate(cropped_videos):
            input_file = f'output_{i}.csv'
            logging.debug(f"Reading input file: {input_file}")
            with open(input_file, 'r') as infile:
                reader = csv.reader(infile)
                next(reader)  
                for row in reader:
                    writer.writerow(row)

if __name__ == "__main__":
    main()