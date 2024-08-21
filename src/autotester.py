import os
from colordetector import ColorDetector

base_dir = r"D:\Testonland\TestResultsOrganized"
a_values = [0.0, -0.05, -0.1, -0.15, -0.2]
frequencies = [0.1, 0.2, 0.3, 0.4, 0.5]

def process_video(video_path, color, amp, freq, a, percentage):
    max_objects = 12 if color == 'green' else 2
    detector = ColorDetector([video_path], color, max_objects, amp, freq, a, percentage)
    detector.run(video_path, 0)

def main():
    amp = 400
    percentage = 5

    for a in a_values:
        for freq in frequencies:
            folder_name = f"a={a}_f={freq}"
            folder_path = os.path.join(base_dir, folder_name)
            
            if os.path.exists(folder_path):
                for video_file in os.listdir(folder_path):
                    if video_file.startswith("cam"):
                        video_path = os.path.join(folder_path, video_file)
                        color = "green" if "cam1" in video_file else "blue"
                        process_video(video_path, color, amp, freq, a, percentage)

if __name__ == "__main__":
    main()