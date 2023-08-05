#!/usr/bin/env python3

import time
import json
from enviroplus import gas
import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

# Define a class to handle JSON logging
class JSONLogger():
    def __init__(self, filename):
        self.filename = filename  # The filename for the log

    # Method to write a dictionary object as JSON to the log file
    def log(self, data):
        with open(self.filename, 'a') as f:  # Open the file
            json.dump(data, f)  # Write the data as JSON
            f.write('\n')  # Add a newline at the end

# Create LCD class instance.
disp = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display.
disp.begin()

# Width and height to calculate text position.
WIDTH = disp.width
HEIGHT = disp.height

# Text settings.
font_size = 12  # Decreased font size for more info on display
font = ImageFont.truetype(UserFont, font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)

# Create an instance of the logger
json_logger = JSONLogger('log.json')

print("""Print readings from the MICS6814 Gas sensor and LTR559 Light & Proximity sensor.
Press Ctrl+C to exit!
""")

try:
    while True:
        gas_readings = gas.read_all()  # Get the gas sensor readings

        # Get the light and proximity readings
        lux = float(ltr559.get_lux())
        prox = float(ltr559.get_proximity())

        # Manually create a dictionary from the readings
        readings_dict = {
            "oxidising": gas_readings.oxidising,
            "reducing": gas_readings.reducing,
            "nh3": gas_readings.nh3,
            "lux": lux,
            "proximity": prox,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        }

        print(readings_dict)  # Print the readings

        json_logger.log(readings_dict)  # Log the readings as JSON

        # New canvas to draw on.
        img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        message = "Ox: {:.2f} Red: {:.2f} NH3: {:.2f} Lux: {:.2f} Prox: {:.2f}".format(
            gas_readings.oxidising, gas_readings.reducing, gas_readings.nh3, lux, prox
        )

        size_x, size_y = draw.textsize(message, font)

        # Calculate text position
        x = (WIDTH - size_x) / 2
        y = (HEIGHT / 2) - (size_y / 2)

        # Draw background rectangle and write text.
        draw.rectangle((0, 0, 160, 80), back_colour)
        draw.text((x, y), message, font=font, fill=text_colour)
        disp.display(img)

        time.sleep(1.0)  # Sleep for a second
except KeyboardInterrupt:
    # Turn off backlight on control-c
    disp.set_backlight(0)
