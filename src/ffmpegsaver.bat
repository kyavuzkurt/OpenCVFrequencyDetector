@echo off
setlocal EnableDelayedExpansion

:: Define the base directory and parameters
set base_dir=E:\TestonLand
set a_values=-0.20
set frequencies=0.1 0.2 0.3 0.4 0.5
set amplitude=400

:: Loop through the values
for %%a in (%a_values%) do (
    for %%f in (%frequencies%) do (
        for %%c in (cam1 cam2) do (
            if "%%c"=="cam1" (
                set color=green
            ) else (
                set color=blue
            )
            set cam_dir=!base_dir!\For_a=%%a\Amplitude_400-Frequency_%%f-a_%%a\Amplitude_between_0-400\Kamera\%%c
            echo Processing directory: !cam_dir!
            
            :: Change directory to the location of your videos
            cd /d "!cam_dir!"
            
            :: Create a temporary file list for FFmpeg
            set fileList="mylist.txt"
            (
                for %%i in (GX01*.MP4) do echo file '%%i'
                for %%i in (GX02*.MP4) do echo file '%%i'
                for %%i in (GX03*.MP4) do echo file '%%i'
            ) > !fileList!
            
            :: Run FFmpeg to concatenate the videos with GPU processing
            ffmpeg -hwaccel cuda -f concat -safe 0 -i !fileList! -c:v h264_nvenc -b:v 5M output.mp4
            
            :: Clean up
            del !fileList!
            
            echo Videos have been concatenated into output.mp4
        )
    )
)

pause