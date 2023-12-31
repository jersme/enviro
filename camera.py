"""
Capture and Rotate Images with Raspberry Pi

This script captures images using a camera connected to a Raspberry Pi, rotates them by a specified angle, and saves them to a specified directory. The images are captured at regular intervals defined by the sleep time.

How to Run:
1. Install the Pillow library: pip install pillow
2. Save this code as a file, e.g., capture_images.py
3. Run the script with the command:
   python capture_images.py --directory /path/to/save/images --sleep_time 60 --rotation_angle 90

Arguments:
- --directory: Specifies the directory where the images will be saved (default: '/mnt/nas').
- --sleep_time: Specifies the time in seconds to wait between capturing images (default: 60).
- --rotation_angle: Specifies the angle in degrees by which the image will be rotated (default: 90).

If no arguments are provided, the script will use the default values.
"""

import subprocess
import time
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import argparse

def rotate_image(image_path, angle):
    with Image.open(image_path) as img:
        rotated_img = img.rotate(angle, expand=True)
        rotated_img.save(image_path)

def add_text_to_image(image_path, location, timestamp):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)

        # Define font and text
        font = ImageFont.load_default()
        text = f"{location} - {timestamp}"

        # Get text size
        text_width, text_height = draw.textsize(text, font)

        # Define text position
        x = img.width - text_width - 10
        y = img.height - text_height - 10

        # Draw text on image
        draw.text((x, y), text, font=font)

        # Save the updated image
        img.save(image_path)

def capture_image(output_path, rotation_angle, location):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        result = subprocess.run(['libcamera-still', '-o', output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        if result.returncode == 0:
            print(f'Image captured successfully. Saved to {output_path}.')
            add_text_to_image(output_path, location, timestamp)
            rotate_image(output_path, rotation_angle)
        else:
            print(f'Failed to capture image. Error: {result.stderr.decode()}')
    except subprocess.TimeoutExpired:
        print('Capture timed out.')
    except Exception as e:
        print(f'An unexpected error occurred: {str(e)}')

def capture_and_rotate_images_periodically(directory, sleep_time, rotation_angle, location):
    if not os.path.exists(directory):
        os.makedirs(directory)
    while True:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'{directory}/image_{timestamp}.jpg'
        capture_image(output_path, rotation_angle, location)
        time.sleep(sleep_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture and rotate images.")
    parser.add_argument('--directory', type=str, default='/mnt/nas', help='Directory to save captured images.')
    parser.add_argument('--sleep_time', type=int, default=60, help='Time to sleep between captures in seconds.')
    parser.add_argument('--rotation_angle', type=int, default=90, help='Angle to rotate the image in degrees.')
    parser.add_argument('--location', type=str, default='Amsterdam, The Netherlands', help='Location to add to the image.')
    args = parser.parse_args()
    capture_and_rotate_images_periodically(args.directory, args.sleep_time, args.rotation_angle, args.location)
