import tkinter as tk
from tkinter import filedialog, messagebox, ttk  
from ttkbootstrap.tooltip import ToolTip  
import cv2 as cv
import numpy as np
import colordetector as cd
import plotter

def first_frame_extraction(video_path):
    video = cv.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video. Path: {video_path}")
        return False
    first_frame = video.read()[1]
    
    def apply_hsv_filter(frame, hsv_values):
        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower_bound = np.array(hsv_values[:3])
        upper_bound = np.array(hsv_values[3:])
        mask = cv.inRange(hsv_frame, lower_bound, upper_bound)
        result = cv.bitwise_and(frame, frame, mask=mask)
        return result

    def on_trackbar(val):
        hsv_values = [cv.getTrackbarPos(f'{label}', 'HSV Range Selector') for label in labels]
        filtered_frame = apply_hsv_filter(first_frame, hsv_values)
        combined_frame = cv.hconcat([first_frame, filtered_frame])
        resized_frame = cv.resize(combined_frame, (combined_frame.shape[1] // 2, combined_frame.shape[0] // 2))
        cv.imshow("First Frame and Filtered Frame", resized_frame)

    if first_frame is not False:
        cv.putText(first_frame, "Press 'q' to close and save HSV values", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        labels = ['Hue Min', 'Saturation Min', 'Value Min', 'Hue Max', 'Saturation Max', 'Value Max']
        cv.namedWindow('HSV Range Selector')
        for i, label in enumerate(labels):
            cv.createTrackbar(label, 'HSV Range Selector', 0, 255, on_trackbar)
        
        on_trackbar(0)  
        while True:
            if cv.waitKey(1) & 0xFF == ord('q'):
                hsv_values = [cv.getTrackbarPos(f'{label}', 'HSV Range Selector') for label in labels]
                hsv_string = ''.join(f'{value:03}' for value in hsv_values)
                break
        cv.destroyAllWindows()
    return hsv_string

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    if file_path:
        video_path_entry.delete(0, tk.END)
        video_path_entry.insert(0, file_path)

def preview():
    video_path = video_path_entry.get()
    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return
    global color_code
    color_code = first_frame_extraction(video_path)

def show_progress_window(total_frames):
    progress_window = tk.Toplevel(root)
    progress_window.title("Processing Video")
    tk.Label(progress_window, text="Processing...").pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate', maximum=total_frames)
    progress_bar.pack(pady=10)
    return progress_window, progress_bar

def update_progress(progress_bar, value):
    progress_bar['value'] = value
    root.update_idletasks()

def run_main():
    video_path = video_path_entry.get()
    preview_enabled = preview_var.get()
    max_objects = max_objects_var.get()
    run_plotter = plotter_var.get()  # Get the state of the plotter checkbox
    
    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return
    
    try:
        max_objects = int(max_objects)
    except ValueError:
        messagebox.showerror("Error", "Max objects must be an integer.")
        return
    
    total_frames = cd.get_total_frames(video_path)
    progress_window, progress_bar = show_progress_window(total_frames)
    
    detector = cd.ColorDetector(video_path, max_objects, color_code, preview_enabled, progress_bar)
    detector.run()
    
    progress_window.destroy()
    
    if run_plotter:
        plotter.run()

root = tk.Tk()
root.title("Video Processing")

tk.Label(root, text="Video Path:").grid(row=0, column=0, padx=10, pady=10)
video_path_entry = tk.Entry(root, width=50)
video_path_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)

preview_var = tk.BooleanVar()
preview_checkbutton = tk.Checkbutton(root, text="Processing Preview Enabled", variable=preview_var)
preview_checkbutton.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
ToolTip(preview_checkbutton, text="When processing Preview Enabled is checked, video will not be saved.")

tk.Label(root, text="Max Objects:").grid(row=2, column=0, padx=10, pady=10)
max_objects_var = tk.StringVar()
tk.Entry(root, textvariable=max_objects_var).grid(row=2, column=1, padx=10, pady=10)

plotter_var = tk.BooleanVar()
plotter_checkbutton = tk.Checkbutton(root, text="Run Plotter", variable=plotter_var)
plotter_checkbutton.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
ToolTip(plotter_checkbutton, text="When Run Plotter is checked, the plotter will run after the video is processed.") 

tk.Button(root, text="Run", command=run_main).grid(row=4, column=0, columnspan=2, padx=10, pady=10)
tk.Button(root, text="Select Color Range", command=preview).grid(row=4, column=2, padx=10, pady=10)

root.mainloop()

