#!/usr/bin/env python3

import time
import sqlite3
from enviroplus import gas
from bme280 import BME280
from smbus import SMBus
import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont

try:
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

# BME280 and SMBus setup
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# Function to retrieve the CPU temperature for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp

factor = 2.25  # Tuning factor for compensation
cpu_temps = [get_cpu_temperature()] * 5

# ST7735 Display setup
disp = ST7735.ST7735(port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=10000000)
disp.begin()
WIDTH = disp.width
HEIGHT = disp.height

# Text settings
font_size = 10
font = ImageFont.truetype(UserFont, font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)

# Update time text settings
update_time_font_size = 8
update_time_font = ImageFont.truetype(UserFont, update_time_font_size)

# SQLite setup
conn = sqlite3.connect('sensor_readings.db')
cursor = conn.cursor()

# Create table if not already existing
cursor.execute('''
    CREATE TABLE IF NOT EXISTS readings
    (timestamp TEXT, oxidising REAL, reducing REAL, nh3 REAL, lux REAL, proximity REAL, compensated_temperature REAL, pressure REAL, humidity REAL)
''')

print("Press Ctrl+C to exit!")

messages = []
message_index = 0

try:
    while True:
        # Gather sensor readings
        gas_readings = gas.read_all()
        lux = float(ltr559.get_lux())
        prox = float(ltr559.get_proximity())

        # Calculate compensated temperature
        cpu_temp = get_cpu_temperature()
        cpu_temps = cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        raw_temp = bme280.get_temperature()
        comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)

        # Retrieve additional weather data
        pressure = bme280.get_pressure()
        humidity = bme280.get_humidity()

        # Prepare and insert data into SQLite database
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        cursor.execute('INSERT INTO readings VALUES (?,?,?,?,?,?,?,?,?)', (current_time, gas_readings.oxidising, gas_readings.reducing, gas_readings.nh3, lux, prox, comp_temp, pressure, humidity))
        conn.commit()

        # Prepare readings for display
        messages = [
            "Ox: {:.2f}".format(gas_readings.oxidising),
            "Red: {:.2f}".format(gas_readings.reducing),
            "NH3: {:.2f}".format(gas_readings.nh3),
            "Lux: {:.2f}".format(lux),
            "Prox: {:.2f}".format(prox),
            "Temp: {:.2f} *C".format(comp_temp),
            "Pressure: {:.2f} hPa".format(pressure),
            "Humidity: {:.2f} %".format(humidity)
        ]

        # Create image, draw background and sensor readings text
        img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, 160, 80), back_colour)
        
        # Adjust the y-position for main message
        y = (HEIGHT / 4) - (font_size / 2)  
        draw.text((0, y), messages[message_index], font=font, fill=text_colour)
        
        # Draw update time below main message
        update_time_y = y + font_size + 5
        draw.text((0, update_time_y), "Updated: {}".format(current_time), font=update_time_font, fill=text_colour)
        
        disp.display(img)

        # Rotate messages
        message_index = (message_index + 1) % len(messages)

        time.sleep(30.0)

except KeyboardInterrupt:
    disp.set_backlight(0)  # Turn off backlight on exit

finally:
    conn.close()  # Close SQLite connection
