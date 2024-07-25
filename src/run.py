import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("MP4 files", "*.MP4"), ("MP4 files", "*.mp4"),("AVI files", "*.avi"), ("MOV files", "*.mov"), ("MKV files", "*.mkv")])
    if filename:
        video_path.set(filename)

def run_main():
    video = video_path.get()
    color = color_var.get()
    amp = amp_var.get()
    f = f_var.get()
    a = a_var.get()
    m = m_var.get()
    p = p_var.get()
    plot = plot_var.get()
    if color == 'green':
        color_number = 1
    elif color == 'blue':
        color_number = 2
    
    if not video or not color or not m:
        messagebox.showerror("Error", "Please fill in required fields.")
        return

    command = f"python main.py --video {video} --color {color} --amp {amp} --f {f} --a {a} --m {m} --p {p}"
    masked_command = f"python maskedvideoexport.py --video_path {video} --color_number {color_number} --amp {amp} --f {f} --a {a} --p {p}"
    bounding_command = f"python bounding_box_video.py --video_path {video} --color_number {color_number} --amp {amp} --f {f} --a {a} --p {p}"
    
    processes = []
    try:
        #processes.append(subprocess.Popen(command, shell=True))
        #processes.append(subprocess.Popen(masked_command, shell=True))
        processes.append(subprocess.Popen(bounding_command, shell=True))
        
        if plot:
            processes.append(subprocess.Popen("python plotter.py", shell=True))
        
        for process in processes:
            process.wait()
        
        messagebox.showinfo("Success", "All processes completed successfully.")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

app = tk.Tk()
app.title("Color Detector GUI")

tk.Label(app, text="Select Video File:").grid(row=0, column=0, padx=10, pady=10)
video_path = tk.StringVar()
tk.Entry(app, textvariable=video_path, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(app, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="Select Color:").grid(row=1, column=0, padx=10, pady=10)
color_var = tk.StringVar()
color_dropdown = tk.OptionMenu(app, color_var, "blue", "green")
color_dropdown.grid(row=1, column=1, padx=10, pady=10)

tk.Label(app, text="Amplitude (amp):").grid(row=2, column=0, padx=10, pady=10)
amp_var = tk.DoubleVar()
tk.Entry(app, textvariable=amp_var).grid(row=2, column=1, padx=10, pady=10)

tk.Label(app, text="Frequency (f):").grid(row=3, column=0, padx=10, pady=10)
f_var = tk.DoubleVar()
tk.Entry(app, textvariable=f_var).grid(row=3, column=1, padx=10, pady=10)

tk.Label(app, text="a variable:").grid(row=4, column=0, padx=10, pady=10)
a_var = tk.DoubleVar(value=0)
tk.Entry(app, textvariable=a_var).grid(row=4, column=1, padx=10, pady=10)

tk.Label(app, text="Select number of objects:").grid(row=5, column=0, padx=10, pady=10)
m_var = tk.IntVar()
tk.Entry(app, textvariable=m_var).grid(row=5, column=1, padx=10, pady=10)

tk.Label(app, text="Percentage:").grid(row=6, column=0, padx=10, pady=10)
p_var = tk.DoubleVar()
tk.Entry(app, textvariable=p_var).grid(row=6, column=1, padx=10, pady=10)


tk.Label(app, text="Plot results:").grid(row=7, column=0, padx=10, pady=10)
plot_var = tk.BooleanVar()
tk.Checkbutton(app, text="Yes", variable=plot_var).grid(row=7, column=1, padx=10, pady=10)

tk.Button(app, text="Run", command=run_main).grid(row=8, column=0, columnspan=3, pady=20)
tk.Button(app, text="Exit", command=app.quit).grid(row=8, column=2, columnspan=3, pady=10)

app.mainloop()