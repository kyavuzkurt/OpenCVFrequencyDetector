# Video Processing and Frequency Detection

## Requirements

To run the code, you need to install the required Python packages. You can install them using the following command:

```sh
pip install -r requirements.txt
```

## Usage

### Video Cropping and Frequency Detection

The main script for video cropping and frequency detection is `main.py`. It processes a video file, crops regions of interest, and analyzes the cropped segments. Change the initial HSV values from `main.py` and `colordetector.py` to your desired values to be tracked.

#### Running the Script

```sh
python main.py --video path/to/your/video.mp4
```

### Template Management

The `trackerdemo.py` script provides functionalities for creating, loading, and deleting templates for object tracking.

#### Running the Script

```sh
python trackerdemo.py --video path/to/your/video.mp4 --tracker kcf
```

### Color Tracking Demo

The `colortrackerdemo.py` script demonstrates color-based object tracking using predefined HSV ranges.

#### Running the Script

```sh
python colortrackerdemo.py --video path/to/your/video.mp4
```

## Logging

The scripts use Python's `logging` module to log debug information. The log level is set to `DEBUG` to provide detailed information about the execution.

## Output

The scripts generate CSV files containing the detected object coordinates and other relevant data. The output files are named based on the current date and time to ensure uniqueness.

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

