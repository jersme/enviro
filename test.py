#!/usr/bin/env python3

import time
import json
from enviroplus import gas

class JSONLogger():
    def __init__(self, filename):
        self.filename = filename

    def log(self, data):
        with open(self.filename, 'a') as f:
            json.dump(data, f)
            f.write('\n')

json_logger = JSONLogger('log.json')

print("""gas.py - Print readings from the MICS6814 Gas sensor.

Press Ctrl+C to exit!

""")

try:
    while True:
        readings = gas.read_all()
        # convert the readings object to a dictionary if it's not
        if not isinstance(readings, dict):
            readings = readings.__dict__
        # add a timestamp to your readings
        readings["timestamp"] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        json_logger.log(readings)
        time.sleep(1.0)
except KeyboardInterrupt:
    pass

