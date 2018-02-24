import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from time import sleep, time, strftime
import _thread
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from copreus.drivers.epaper import EPaper, EPaperConstants, EPaperMQTTMessageConverter
from tests.tools import get_mqtt, get_model
import RPi.GPIO as GPIO

filename = 'config_epaper.yaml'
font_file = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"
model = get_model(filename)

#_ep_thread = _thread.start_new_thread(EPaper.standalone, (('-c', filename,'-v'),))
_ep_thread = _thread.start_new_thread(EPaper.standalone, (('-c', filename),))

mqtt = get_mqtt(filename)
mqtt.connect()

font_small = ImageFont.truetype(font_file, 12)
font_large = ImageFont.truetype(font_file, 64)

sleep(1)

display_width = EPaperConstants.model[model]["height"]
display_height = EPaperConstants.model[model]["width"]

base_image = Image.new('1', (display_width, display_height), 255)  # 255: clear the frame
draw = ImageDraw.Draw(base_image)
draw.rectangle((0, 10, display_width, 32), fill=0)
draw.text((30, 16), 'e-Paper Demo', font=font_small, fill=255)
print("initializing epaper")
msg = EPaperMQTTMessageConverter.to_full_image(base_image)
mqtt.client.publish("/w/thermostat/display/full_image_twice", msg)

sleep(1)

time_large = Image.new('1', (205, 80), 255)  # 255: clear the frame
draw_large = ImageDraw.Draw(time_large)
time_small = Image.new('1', (56, 16), 0)
draw_small = ImageDraw.Draw(time_small)


large_width, large_height = time_large.size
small_width, small_height = time_small.size

while True:
    t = strftime('%H:%M')

    draw_large.rectangle((0, 0, large_width, large_height), fill=255)
    draw_large.text((0, 0), t, font=font_large, fill=0)

    draw_small.rectangle((0, 0, small_width, small_height), fill=0)
    draw_small.text((0,0), t, font=font_small, fill=255)

    list = [
        {
            "x": int((display_width-large_width)/2),
            "y": 40,
            "image": time_large
        },
        {
            "x": display_width-small_width-16,
            "y": 16,
            "image": time_small
        }
    ]
    msg = EPaperMQTTMessageConverter.to_partial_images(list)
    print("updating time to '{}'".format(t))
    mqtt.client.publish("/w/thermostat/display/part_image", msg)

    ct = time()
    current_second = int(ct) * 1000
    current_ms = int(ct * 1000.0)

    step_target = 60
    step = (step_target - ct % step_target)
    step_safety = 1

    diff = step + ((current_ms - current_second) / 1000.0) # wait this for the next ms ...

    print("sleeping for {} seconds.".format(diff+step_safety))
    sleep(diff + step_safety)

sleep(2)
GPIO.cleanup()



