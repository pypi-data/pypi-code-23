import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from time import sleep

from PIL import Image

from copreus.drivers.epaper import EPaperMQTTMessageConverter
from tests.tools import get_mqtt

print("send the given png to the epaper")

filename = 'config_epaper.yaml'

mqtt = get_mqtt(filename)
mqtt.connect()

png = Image.open("gui_v2.png")
msg_png = EPaperMQTTMessageConverter.to_full_image(png)

print("send png image")
mqtt.client.publish("/w/wohnzimmer/thermostat/display/full_image_twice", msg_png)

sleep(2)

mqtt.disconnect()
print("done")
