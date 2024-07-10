# Multi-Object Tracker

This project uses OpenCV to track multiple objects in a video stream. The objects can be manually selected by the user, and their positions are logged over time in a CSV file. The tracker supports different tracking algorithms and can initialize object selection before starting the video stream.

## Requirements

To run this project, you need the following libraries:

- OpenCV
- imutils

You can install these dependencies using pip:

```bash
pip install opencv-python opencv-contrib-python imutils
```

## Functions

### Key Features

- **Multi-object tracking**: Track multiple objects simultaneously.
- **Manual object selection**: Allows the user to manually select objects to be tracked.
- **Different tracker types**: Supports various OpenCV tracking algorithms (CSRT, KCF, MIL).
- **Data logging**: Logs the positions of the tracked objects over time in a CSV file.
- **Initialization mode**: Allows object selection before starting the video stream.

### Code Breakdown

- **Object Trackers**: Define the available OpenCV object trackers.
- **Video Stream Initialization**: Start video stream from webcam or video file.
- **Object Selection**: Allows manual selection of objects to be tracked.
- **Tracking and Logging**: Tracks objects frame by frame and logs their positions in a CSV file.

## Usage

### Command Line Arguments

- `--video`: Path to input video file. If not provided, the webcam is used.
- `--tracker`: OpenCV object tracker type (default is `kcf`). Options: `csrt`, `kcf`, `mil`.
- `--init`: Initialize object selection before starting the video.

### Running the Code

1. **Using Webcam**

    To start tracking using the webcam with the default tracker (KCF):

    ```bash
    python multi_object_tracker.py
    ```

    To initialize object selection before starting the video:

    ```bash
    python multi_object_tracker.py --init
    ```

2. **Using Video File**

    To start tracking using a video file:

    ```bash
    python3 multi_object_tracker.py --video path/to/your/video.mp4
    ```

    To initialize object selection before starting the video:

    ```bash
    python3 multi_object_tracker.py --video path/to/your/video.mp4 --init
    ```

### Controls

- Press `s` to select a new object to track during the video stream.
- Press `q` to quit the video stream.

### Output

The positions of the tracked objects are logged in a CSV file located in the `logs` directory (one level up from the script's directory). The filename is in the format `DD-MM-YYYY-HH:MM:SS.csv`.

### Example CSV Output

The CSV file contains the following columns:

```
time,x1,y1,x2,y2,...,x12,y12
```

Each row represents a frame, with the positions of up to 12 tracked objects and the timestamp.

---

If you need any further adjustments or have additional content to add, feel free to let me know!
