import subprocess
import time
import os
from datetime import datetime

def capture_image(output_path):
    try:
        # Run the libcamera-still command to capture an image
        result = subprocess.run(['libcamera-still', '-o', output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)

        # Check if the command was successful
        if result.returncode == 0:
            print(f'Image captured successfully. Saved to {output_path}.')
        else:
            print(f'Failed to capture image. Error: {result.stderr.decode()}')
    except subprocess.TimeoutExpired:
        print('Capture timed out.')
    except Exception as e:
        print(f'An unexpected error occurred: {str(e)}')

def capture_images_every_minute(directory):
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    while True:
        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Construct the output path using the timestamp
        output_path = f'{directory}/image_{timestamp}.jpg'

        # Capture the image
        capture_image(output_path)

        # Wait for 60 seconds before capturing the next image
        time.sleep(60)

# Directory to save the captured images
directory = '/home/jeroen/camtest/series'

# Start capturing images every minute
capture_images_every_minute(directory)
