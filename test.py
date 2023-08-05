#!/usr/bin/env python3

import time
import json
from enviroplus import gas
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

        time.sleep(1.0)  # Sleep for a second
except KeyboardInterrupt:
    pass


