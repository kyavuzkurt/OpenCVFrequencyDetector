import os
import subprocess
from colordetector import ColorDetector
import tempfile

base_dir = r"C:\Tests"
a_values = [-0.10, -0.15]
frequencies = [0.1, 0.2, 0.3, 0.4, 0.5]
amplitude = 400

def process_video(video_path, color, amp, freq, a, percentage):
    max_objects = 12 if color == 'green' else 2
    detector = ColorDetector([video_path], color, max_objects, amp, freq, a, percentage)
    detector.run(video_path, 0)

def check_and_process(cam_dir, color, amp, freq, a):
    
    output_file = os.path.join(cam_dir, "output.mp4")
    process_video(output_file, color, amp, freq, a, 5)  

def main():
    for a in a_values:
        for freq in frequencies:
            for cam in ["cam1", "cam2"]:
                color = "green" if cam == "cam1" else "blue"
                cam_dir = os.path.join(base_dir, f"For_a={a}", f"Amplitude_400-Frequency_{freq}-a_{a}", "Amplitude_between_0-400", "Kamera", cam)
                check_and_process(cam_dir, color, amplitude, freq, a)

if __name__ == "__main__":
    main()