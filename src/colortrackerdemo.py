from imutils.video import VideoStream
import argparse
import time
import cv2 as cv
import datetime
import os
import csv
import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import numpy as np

# Argument parsing
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, help="path to input video file")
args = vars(ap.parse_args())

# Log directory and file setup
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logs")
os.makedirs(logs_dir, exist_ok=True)
now = datetime.datetime.now()
output_file = os.path.join(logs_dir, now.strftime("%d-%m-%Y-%H:%M:%S") + ".csv")

# Write CSV header
with open(output_file, "w", newline='') as f:
    writer = csv.writer(f)
    header = ["frame"]
    for i in range(1, 13):  # Maximum of 12 objects
        header.extend([f"x{i}", f"y{i}"])
    writer.writerow(header)

# Initialize video stream
if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    vs = cv.VideoCapture(args["video"])


# Template functions
def save_template(template_name, initial_boxes):
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "colortemplate"))
    os.makedirs(templates_dir, exist_ok=True)

    # Determine the next template ID
    existing_templates = [f for f in os.listdir(templates_dir) if f.endswith(".json")]
    next_template_id = len(existing_templates) + 1

    template_file = os.path.join(templates_dir, f"{next_template_id}.json")
    with open(template_file, "w") as f:
        json.dump({"name": template_name, "boxes": initial_boxes}, f)


def load_template(template_id):
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "colortemplate"))
    template_file = os.path.join(templates_dir, f"{template_id}.json")
    with open(template_file, "r") as f:
        template_data = json.load(f)
    return template_data


def delete_template(template_id):
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "colortemplate"))
    template_file = os.path.join(templates_dir, f"{template_id}.json")
    if os.path.exists(template_file):
        os.remove(template_file)
        return True
    return False


def list_templates():
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "colortemplate"))
    os.makedirs(templates_dir, exist_ok=True)
    templates = []
    for filename in os.listdir(templates_dir):
        if filename.endswith(".json"):
            with open(os.path.join(templates_dir, filename), "r") as f:
                template_data = json.load(f)
                templates.append({"id": filename[:-5], "name": template_data["name"]})
    return templates


# Tkinter UI for template selection/creation
root = tk.Tk()
root.withdraw()  # Hide the main window

action = simpledialog.askstring("Input",
                                "Choose an action: Create a new template (C), Load a template (L), Delete a template (D)")

initial_boxes = []

if action == 'C':
    template_name = simpledialog.askstring("Input", "Enter the template name:")
    object_count = simpledialog.askinteger("Input", "Enter the number of objects to track:", minvalue=1, maxvalue=12)
    for i in range(object_count):
        x = simpledialog.askinteger("Input", f"Enter the initial x coordinate for object {i + 1}:")
        y = simpledialog.askinteger("Input", f"Enter the initial y coordinate for object {i + 1}:")
        initial_boxes.append((x, y, 50, 50))  # Create a box centered around (x, y)
    save_template(template_name, initial_boxes)
elif action == 'L':
    templates = list_templates()
    if not templates:
        messagebox.showinfo("Info", "No templates available.")
        exit()
    template_choices = "\n".join([f"{template['id']}: {template['name']}" for template in templates])
    selected_template_id = simpledialog.askstring("Input",
                                                  f"Available templates:\n{template_choices}\nEnter the template ID to load:")
    template_data = load_template(selected_template_id)
    initial_boxes = template_data["boxes"]
elif action == 'D':
    templates = list_templates()
    if not templates:
        messagebox.showinfo("Info", "No templates available.")
        exit()
    template_choices = "\n".join([f"{template['id']}: {template['name']}" for template in templates])
    selected_template_id = simpledialog.askstring("Input",
                                                  f"Available templates:\n{template_choices}\nEnter the template ID to delete:")
    if delete_template(selected_template_id):
        messagebox.showinfo("Info", f"Template {selected_template_id} deleted successfully.")
    else:
        messagebox.showinfo("Info", f"Template {selected_template_id} not found.")
    exit()



def color_tracker(frame, initial_boxes, lower_bound, upper_bound):
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    mask = cv.inRange(hsv, lower_bound, upper_bound)

    tracked_boxes = []
    for (x, y, w, h) in initial_boxes:
        roi = mask[y:y + h, x:x + w]
        contours, _ = cv.findContours(roi, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv.contourArea)
            (x, y, w, h) = cv.boundingRect(c)
            tracked_boxes.append((x, y, w, h))
        else:
            tracked_boxes.append((x, y, w, h))

    return tracked_boxes


lower_bound = np.array([30, 100, 50])
upper_bound = np.array([90, 255, 255])


if not initial_boxes:
    initial_boxes = [(50, 50, 100, 100), (150, 150, 100, 100)]


fps = vs.get(cv.CAP_PROP_FPS) if args.get("video", False) else 30
frame_count = 0
start_time = time.time()

while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame

    if frame is None:
        break

    frame_count += 1
    elapsed_time = time.time() - start_time
    current_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

    data = [frame_count]
    tracked_boxes = color_tracker(frame, initial_boxes, lower_bound, upper_bound)  # Call color tracker function

    # Draw tracked boxes
    for (x, y, w, h) in tracked_boxes:
        cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display FPS
    cv.putText(frame, f"FPS: {current_fps:.2f}", (10, frame.shape[0] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0),
               2)

    # Update data for CSV
    for (x, y, w, h) in tracked_boxes:
        data.append(x)
        data.append(y)

    data.extend([''] * (25 - len(data)))  # Ensure data has the correct length

    with open(output_file, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

    cv.imshow("Frame", frame)
    key = cv.waitKey(1) & 0xFF

    if key == ord("q"):
        break

vs.release()
cv.destroyAllWindows()