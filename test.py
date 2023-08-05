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

try:
    while True:
        readings = gas.read_all()
        # manually create a dictionary from the readings
        readings_dict = {
            "oxidising": readings.oxidising,
            "reducing": readings.reducing,
            "nh3": readings.nh3,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        }
        json_logger.log(readings_dict)
        time.sleep(1.0)
except KeyboardInterrupt:
    pass

