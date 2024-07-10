from imutils.video import VideoStream
import argparse
import time
import cv2 as cv
import datetime
import os
import csv

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf", help="OpenCV object tracker type")
ap.add_argument("-i", "--init", action="store_true", help="Initialize object selection before starting video")
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

if args.get("init", False):
    if not args.get("video", False):
        frame = vs.read()
    else:
        ret, frame = vs.read()

    if frame is not None:
        while True:
            box = cv.selectROI("Frame", frame, False, False)
            tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
            trackers.add(tracker, frame, box)
            object_count += 1
            key = cv.waitKey(0) & 0xFF
            if key == ord("q"):
                break
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

    if key == ord("s") and not args.get("init", False):
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
