import subprocess

def capture_image(output_path):
    # Run the libcamera-still command to capture an image
    result = subprocess.run(['libcamera-still', '-o', output_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the command was successful
    if result.returncode == 0:
        print(f'Image captured successfully. Saved to {output_path}.')
    else:
        print(f'Failed to capture image. Error: {result.stderr.decode()}')

# Path to save the captured image
output_path = '/path/to/your/image.jpg'

# Capture the image
capture_image(output_path)
