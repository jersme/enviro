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

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp

factor = 2.25  # Tuning factor for compensation
cpu_temps = [get_cpu_temperature()] * 5

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

# Text settings.
font_size = 10
font = ImageFont.truetype(UserFont, font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)

# SQLite setup
conn = sqlite3.connect('sensor_readings.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS readings
    (timestamp TEXT, oxidising REAL, reducing REAL, nh3 REAL, lux REAL, proximity REAL, compensated_temperature REAL, pressure REAL, humidity REAL)
''')

print("""Print readings from the MICS6814 Gas sensor, BME280 sensor and LTR559 Light & Proximity sensor.
Press Ctrl+C to exit!
""")

messages = []
message_index = 0

try:
    while True:
        gas_readings = gas.read_all()  # Get the gas sensor readings
        lux = float(ltr559.get_lux())  # Get the light reading
        prox = float(ltr559.get_proximity())  # Get the proximity reading

        cpu_temp = get_cpu_temperature()
        cpu_temps = cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        raw_temp = bme280.get_temperature()
        comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)

        # Get pressure and humidity from BME280
        pressure = bme280.get_pressure()
        humidity = bme280.get_humidity()

        # Construct data tuple for SQLite
        data_tuple = (time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), gas_readings.oxidising, gas_readings.reducing, gas_readings.nh3, lux, prox, comp_temp, pressure, humidity)
        print(data_tuple)  # Print the readings

        # Insert a row of data
        cursor.execute('INSERT INTO readings VALUES (?,?,?,?,?,?,?,?,?)', data_tuple)

        # Commit changes
        conn.commit()

        # Store sensor readings in messages list
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

        # New canvas to draw on.
        img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw background rectangle and write text.
        draw.rectangle((0, 0, 160, 80), back_colour)
        y = (HEIGHT / 2) - (font_size / 2)
        draw.text((0, y), messages[message_index], font=font, fill=text_colour)
        disp.display(img)

        # Update message index to cycle through sensor readings
        message_index = (message_index + 1) % len(messages)

        time.sleep(30.0)  # Sleep for 30 seconds
except KeyboardInterrupt:
    # Turn off backlight on control-c
    disp.set_backlight(0)
finally:
    # Close the connection to the database
    conn.close()
