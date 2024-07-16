import colordetector as cd
import cv2 as cv
import csv
import datetime
import argparse
import subprocess
import concurrent.futures

class FrequencyDetector:

    def get_cropped_videos(self, video_path):
        video_paths = []
        

        def crop_video(i):
            output_path = f"cropped_video_{i}.mp4"
            command = [
                'ffmpeg', '-i', video_path, '-vf',
                f"crop=in_w/12:in_h:{i}*in_w/12:0",
                '-c:a', 'copy', output_path
            ]
            subprocess.run(command, check=True)
            return output_path

        with concurrent.futures.ThreadPoolExecutor() as executor:
            video_paths = list(executor.map(crop_video, range(12)))

        return video_paths
    
    def get_frequency_data(self, video_paths):
        for i, video_path in enumerate(video_paths):
            color_detector = cd.ColorDetector([video_path])
            color_detector.run(video_path, i)  # Pass the video path and index to the run method
            frame_count = color_detector.video.get(cv.CAP_PROP_FRAME_COUNT)
            print(f"Video: {video_path}, Frame Count: {frame_count}")
            color_detector.video.release()

def main():
    parser = argparse.ArgumentParser(description='Frequency Detector')
    parser.add_argument('--video', '-v', type=str, help='Path to the video file', required=True)
    args = parser.parse_args()

    video_path = args.video
    frequency_detector = FrequencyDetector()
    video_paths = frequency_detector.get_cropped_videos(video_path)
    frequency_detector.get_frequency_data(video_paths)

    now = datetime.datetime.now()
    output_file = now.strftime("%d-%m-%Y_%H:%M:%S") + ".csv"

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Frame', 'X', 'Y', 'Width', 'Height'])

        for i, video_path in enumerate(video_paths):
            input_file = f'output_{i}.csv'
            with open(input_file, 'r') as infile:
                reader = csv.reader(infile)
                next(reader)  
                for row in reader:
                    writer.writerow(row)

if __name__ == "__main__":
    main()