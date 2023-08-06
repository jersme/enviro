#!/usr/bin/env python3

import time
import sqlite3
from enviroplus import gas
from bme280 import BME280
from smbus import SMBus
import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont
from pms5003 import PMS5003

try:
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    ltr559 = None

# BME280 and SMBus setup
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# PMS5003 setup
pms5003 = PMS5003(device='/dev/ttyAMA0', baudrate=9600, pin_enable=22, pin_reset=27)

# CPU Temperature function
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp

factor = 2.25  
cpu_temps = [get_cpu_temperature()] * 5

# ST7735 Display setup
disp = ST7735.ST7735(port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=10000000)
disp.begin()  
WIDTH = disp.width
HEIGHT = disp.height

# SQLite setup
conn = sqlite3.connect('values_lindenhoevestraat.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS readings
    (timestamp TEXT, oxidising REAL, reducing REAL, nh3 REAL, lux REAL, proximity REAL, compensated_temperature REAL, pressure REAL, humidity REAL, pm1 REAL, pm2_5 REAL, pm10 REAL)
''')

font_size = 10
font = ImageFont.truetype(UserFont, font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)

messages = []
message_index = 0
reading_count = 0
last_update_time = time.time()

try:
    while True:
        gas_readings = gas.read_all()
        lux = ltr559.get_lux() if ltr559 else 0
        prox = ltr559.get_proximity() if ltr559 else 0

        cpu_temp = get_cpu_temperature()
        cpu_temps = cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        raw_temp = bme280.get_temperature()
        comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)

        pressure = bme280.get_pressure()
        humidity = bme280.get_humidity()
        
        pm_data = pms5003.read()

        data_tuple = (time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), gas_readings.oxidising, gas_readings.reducing, gas_readings.nh3, lux, prox, comp_temp, pressure, humidity, pm_data.pm_ug_per_m3(1.0), pm_data.pm_ug_per_m3(2.5), pm_data.pm_ug_per_m3(10))
        cursor.execute('INSERT INTO readings VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', data_tuple)
        conn.commit()

        reading_count += 1
        time_since_update = int((time.time() - last_update_time) / 60) # in minutes
        last_update_time = time.time()

        messages = ["Ox: {:.2f}".format(gas_readings.oxidising), 
                    "Red: {:.2f}".format(gas_readings.reducing), 
                    "NH3: {:.2f}".format(gas_readings.nh3), 
                    "Lux: {:.2f}".format(lux), 
                    "Prox: {:.2f}".format(prox), 
                    "Temp: {:.2f} *C".format(comp_temp), 
                    "Pressure: {:.2f} hPa".format(pressure),
                    "Humidity: {:.2f} %".format(humidity),
                    "PM1: {:.2f}".format(pm_data.pm_ug_per_m3(1.0)),
                    "PM2.5: {:.2f}".format(pm_data.pm_ug_per_m3(2.5)),
                    "PM10: {:.2f}".format(pm_data.pm_ug_per_m3(10))]
                    
        img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
        
        draw.text((0, 0), messages[message_index], font=font, fill=text_colour)
        draw.text((0, HEIGHT - font_size), "Last: {}m | Count: {}".format(time_since_update, reading_count), font=font, fill=text_colour)

        disp.display(img)

        message_index = (message_index + 1) % len(messages)

        time.sleep(30.0)

except KeyboardInterrupt:
    disp.set_backlight(0)
finally:
    conn.close()
