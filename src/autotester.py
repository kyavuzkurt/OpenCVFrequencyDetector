import os
import subprocess
from colordetector import ColorDetector

base_dir = "C:\Tests"
a_values = [-0.05]
frequencies = [0.2, 0.3, 0.4, 0.5]
amplitude = 400

def process_video(video_path, color, amp, freq, a, percentage):
    max_objects = 12 if color == 'green' else 2
    detector = ColorDetector([video_path], color, max_objects, amp, freq, a, percentage)
    detector.run(video_path, 0)

def check_and_process(cam_dir, color, amp, freq, a):
    output_file = os.path.join(cam_dir, "output.mp4")
    if not os.path.exists(output_file):
        # Run the bash script to concatenate videos
        bash_script = f"""
        @echo off
        setlocal
        cd /d "{cam_dir}"
        set fileList="mylist.txt"
        (
            for %%i in (GX01*.MP4) do echo file '%%i'
            for %%i in (GX02*.MP4) do echo file '%%i'
            for %%i in (GX03*.MP4) do echo file '%%i'
        ) > %fileList%
        ffmpeg -hwaccel cuda -f concat -safe 0 -i %fileList% -c:v h264_nvenc -b:v 5M output.mp4
        del %fileList%
        echo Videos have been concatenated into output.mp4
        pause
        """
        subprocess.run(bash_script, shell=True, check=True)
    
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