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

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf", help="OpenCV object tracker type")
args = vars(ap.parse_args())

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv.legacy.TrackerCSRT_create,
    "kcf": cv.legacy.TrackerKCF_create,
    "mil": cv.legacy.TrackerMIL_create,
}

trackers = cv.legacy.MultiTracker_create()
object_count = 0


def get_current_time_str():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y-%H:%M:%S:%f")


logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logs")
os.makedirs(logs_dir, exist_ok=True)
now = datetime.datetime.now()
output_file = os.path.join(logs_dir, now.strftime("%d-%m-%Y-%H:%M:%S") + ".csv")

with open(output_file, "w", newline='') as f:
    writer = csv.writer(f)
    header = ["time"]
    for i in range(1, 13):  # Maximum of 12 objects
        header.extend([f"x{i}", f"y{i}"])
    writer.writerow(header)

if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    vs = cv.VideoCapture(args["video"])


def save_template(template_name, initial_boxes):
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
    os.makedirs(templates_dir, exist_ok=True)

    # Determine the next template ID
    existing_templates = [f for f in os.listdir(templates_dir) if f.endswith(".json")]
    next_template_id = len(existing_templates) + 1

    template_file = os.path.join(templates_dir, f"{next_template_id}.json")
    with open(template_file, "w") as f:
        json.dump({"name": template_name, "boxes": initial_boxes}, f)


def load_template(template_id):
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
    template_file = os.path.join(templates_dir, f"{template_id}.json")
    with open(template_file, "r") as f:
        template_data = json.load(f)
    return template_data


def delete_template(template_id):
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
    template_file = os.path.join(templates_dir, f"{template_id}.json")
    if os.path.exists(template_file):
        os.remove(template_file)
        return True
    return False


def list_templates():
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
    os.makedirs(templates_dir, exist_ok=True)
    templates = []
    for filename in os.listdir(templates_dir):
        if filename.endswith(".json"):
            with open(os.path.join(templates_dir, filename), "r") as f:
                template_data = json.load(f)
                templates.append({"id": filename[:-5], "name": template_data["name"]})
    return templates


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

if initial_boxes:
    if not args.get("video", False):
        frame = vs.read()
    else:
        ret, frame = vs.read()

    if frame is not None:
        for box in initial_boxes:
            tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
            trackers.add(tracker, frame, box)
        cv.destroyAllWindows()

while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame

    if frame is None:
        break

    (success, boxes) = trackers.update(frame)
    current_time_str = get_current_time_str()

    data = [current_time_str]
    for box in boxes[:12]:
        (x, y, w, h) = [int(v) for v in box]
        data.extend([x, y])
        cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        object_id = (len(data) // 2)
        cv.putText(frame, f"OBJECT_{object_id}", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    data.extend([''] * (25 - len(data)))

    with open(output_file, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

    cv.imshow("Frame", frame)
    key = cv.waitKey(1) & 0xFF

    if key == ord("s"):
        box = cv.selectROI("Frame", frame, True, False)
        tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
        trackers.add(tracker, frame, box)
        object_count += 1
    elif key == ord("q"):
        break

if not args.get("video", False):
    vs.stop()
else:
    vs.release()
cv.destroyAllWindows()
