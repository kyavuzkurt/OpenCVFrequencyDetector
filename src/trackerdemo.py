from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2 as cv

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf", help="OpenCV object tracker type, csrt, kcf, mil")
args = vars(ap.parse_args())

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv.TrackerCSRT_create,
    "kcf": cv.TrackerKCF_create,
    "mil": cv.TrackerMIL_create,
}
tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
initBB = None

print("[INFO] starting video stream...")
vs = None
if args["video"]:
    vs = cv.VideoCapture(args["video"])
else:
    vs = VideoStream(src=0).start()
time.sleep(1.0)

fps = None

try:
    while True:
        frame = vs.read()

        if args["video"]:
            frame = frame[1] if frame is not None else frame

        if frame is None:
            print("[INFO] no frame read from the stream, exiting...")
            break

        frame = imutils.resize(frame, width=500)
        (H, W) = frame.shape[:2]

        info = []  # Initialize info list
        if initBB is not None:
            (success, box) = tracker.update(frame)
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            fps.update()
            fps.stop()
            info = [
                ("Tracker", args["tracker"]),
                ("Success", "Yes" if success else "No"),
                ("FPS", "{:.2f}".format(fps.fps()))
            ]

        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv.putText(frame, text, (10, H - ((i * 20) + 20)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv.imshow("Frame", frame)
        key = cv.waitKey(1) & 0xFF

        if key == ord("s"):
            initBB = cv.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
            tracker.init(frame, initBB)
            fps = FPS().start()
        elif key == ord("q"):
            break
finally:
    if args["video"]:
        vs.release()
    else:
        vs.stop()
    cv.destroyAllWindows()
