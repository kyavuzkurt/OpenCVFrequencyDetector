import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import re

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("MP4 files", "*.MP4"), ("MP4 files", "*.mp4"),("AVI files", "*.avi"), ("MOV files", "*.mov"), ("MKV files", "*.mkv")])
    if filename:
        video_path.set(filename)
        auto_fill_fields(filename)

def auto_fill_fields(filename):
    # Extract the base name of the file
    base_name = filename.split('/')[-1]
    
    # Use regex to find matching patterns
    amp_match = re.search(r'amp(\d+(\.\d+)?)', base_name)
    f_match = re.search(r'f(\d+(\.\d+)?)', base_name)
    a_match = re.search(r'a(\d+(\.\d+)?)', base_name)
    p_match = re.search(r'p(\d+(\.\d+)?)', base_name)
    
    auto_filled = False
    
    if amp_match:
        amp_var.set(float(amp_match.group(1)))
        auto_filled = True
    if f_match:
        f_var.set(float(f_match.group(1)))
        auto_filled = True
    if a_match:
        a_var.set(float(a_match.group(1)))
        auto_filled = True
    if p_match:
        p_var.set(float(p_match.group(1)))
        auto_filled = True
    
    if auto_filled:
        messagebox.showinfo("Auto-fill", "Fields have been auto-filled based on the file name.")

def run_main():
    video = video_path.get()
    color_display = color_var.get()
    color = color_mapping[color_display]
    amp = amp_var.get()
    f = f_var.get()
    a = a_var.get()
    p = p_var.get()
    
    if not video or not color:
        messagebox.showerror("Error", "Please fill in required fields.")
        return

    command = f"python main.py --video {video} --color {color} --amp {amp} --f {f} --a {a} --p {p} "
    try:
        subprocess.run(command, shell=True, check=True)
        
        if plot_var.get():
            subprocess.run("python plotter.py", shell=True, check=True)
        
        messagebox.showinfo("Success", "All processes completed successfully.")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

app = tk.Tk()
app.title("Color Detector GUI")

tk.Label(app, text="Select Video File:").grid(row=0, column=0, padx=10, pady=10)
video_path = tk.StringVar()
tk.Entry(app, textvariable=video_path, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(app, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="Select Color:").grid(row=1, column=0, padx=10, pady=10)
color_var = tk.StringVar()
color_mapping = {"Blue": "blue", "Green": "green"}
color_dropdown = tk.OptionMenu(app, color_var, *color_mapping.keys())
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

tk.Label(app, text="Percentage:").grid(row=5, column=0, padx=10, pady=10)
p_var = tk.DoubleVar()
tk.Entry(app, textvariable=p_var).grid(row=5, column=1, padx=10, pady=10)

tk.Label(app, text="Plot results:").grid(row=6, column=0, padx=10, pady=10)
plot_var = tk.BooleanVar()
tk.Checkbutton(app, text="Yes", variable=plot_var).grid(row=6, column=1, padx=10, pady=10)

tk.Button(app, text="Run", command=run_main).grid(row=7, column=0, columnspan=3, pady=20)
tk.Button(app, text="Exit", command=app.quit).grid(row=7, column=2, columnspan=3, pady=10)

app.mainloop()