"""
README:
This script monitors a camera on Raspberry Pi and records a video when motion is detected.

SETUP for Raspbian 32-bit Lite:
1. Update the system:
   sudo apt-get update
   sudo apt-get upgrade

2. Install required dependencies:
   sudo apt-get install libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test

3. Install pip (if not installed):
   sudo apt-get install python3-pip

4. Install OpenCV:
   sudo pip3 install opencv-contrib-python-headless

5. Install imutils:
   pip3 install imutils

6. Connect a compatible camera to your Raspberry Pi.

RUNNING THE SCRIPT:
You can run the script with the following command:
   python3 script.py --prefix PREFIX --duration DURATION --path PATH

ARGUMENTS:
  --prefix  : Prefix for the video name (default: motion_detected)
  --duration: Recording duration in seconds (default: 30)
  --path    : Path to save the recorded videos (default: current directory)

EXAMPLE:
   python3 script.py --prefix my_video --duration 60 --path /path/to/save

This example will set the video name prefix to 'my_video', recording duration to 60 seconds, and save the videos to '/path/to/save'.
"""

import cv2
import imutils
import time
from datetime import datetime
import argparse
import os

# Argument parser to accept command-line arguments
parser = argparse.ArgumentParser(description="Motion detection and video recording")
parser.add_argument("--prefix", default="motion_detected", help="Prefix for the video name")
parser.add_argument("--duration", type=int, default=30, help="Recording duration in seconds")
parser.add_argument("--path", default=".", help="Path to save the recorded videos")
args = parser.parse_args()

# Set the prefix for the video name, recording duration, and save path
video_prefix = args.prefix
record_duration = args.duration
save_path = args.path

# Create the save path if it does not exist
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Function to detect motion
def detect_motion(frame, prev_frame, min_area=500):
    frame_delta = cv2.absdiff(prev_frame, frame)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) > min_area:
            return True

    return False

# Initialize camera
camera = cv2.VideoCapture(0)

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = None

# Previous frame to compare with current frame
prev_frame = None

# Loop to continuously get frames from camera
while True:
    ret, frame = camera.read()
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if prev_frame is None:
        prev_frame = gray
        continue
    
    if detect_motion(gray, prev_frame):
        if out is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_name = f"{video_prefix}_{timestamp}.avi"
            full_path = os.path.join(save_path, video_name)
            out = cv2.VideoWriter(full_path, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
            start_time = time.time()

        out.write(frame)
        
        # If the record duration has passed, stop recording
        if time.time() - start_time > record_duration:
            out.release()
            out = None

    prev_frame = gray

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Clean up
camera.release()
cv2.destroyAllWindows()
