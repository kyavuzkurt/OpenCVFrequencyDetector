import colordetector as cd
import argparse
import logging
import os
import cv2 as cv
import numpy as np

logging.basicConfig(level=logging.DEBUG)



def main(video_path, max_objects, preview_enabled, color_code):

    logging.info(f"Video Path: {video_path}")
    logging.info(f"Max Objects: {max_objects}")
    logging.info(f"Preview Enabled: {preview_enabled}")
    logging.info(f"Color Code: {color_code}")

    cd.ColorDetector(video_path=video_path, max_objects=max_objects, preview_enabled=preview_enabled, color_code=color_code)
    cd.ColorDetector.run()
if __name__ == "__main__":
    main()