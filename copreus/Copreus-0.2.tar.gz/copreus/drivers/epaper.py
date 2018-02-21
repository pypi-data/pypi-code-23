
## the epaper related business-logic of this class has been taken from:
##
 #  @filename   :   epd2in13.py
 #  @brief      :   Implements for e-paper library
 #  @author     :   Yehui from Waveshare
 #
 #  Copyright (C) Waveshare     September 9 2017
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documnetation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to  whom the Software is
 # furished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 #

import base64
import json
import threading
import queue
from io import BytesIO
from time import sleep

import RPi.GPIO as GPIO
from PIL import Image

from copreus.baseclasses.aspi import ASPI
from copreus.baseclasses.adriver import ADriver
from copreus.baseclasses.aevents import AEvents


class EPaperConstants:
    """Constants provided by Waveshare.

    The dict size contains all support displays (width/height). In the yaml device config the value of attribute 'size' must be
    equivalent to one of the keys in this dict.
    """

    DRIVER_OUTPUT_CONTROL                       = 0x01
    BOOSTER_SOFT_START_CONTROL                  = 0x0C
    GATE_SCAN_START_POSITION                    = 0x0F
    DEEP_SLEEP_MODE                             = 0x10
    DATA_ENTRY_MODE_SETTING                     = 0x11
    SW_RESET                                    = 0x12
    TEMPERATURE_SENSOR_CONTROL                  = 0x1A
    MASTER_ACTIVATION                           = 0x20
    DISPLAY_UPDATE_CONTROL_1                    = 0x21
    DISPLAY_UPDATE_CONTROL_2                    = 0x22
    WRITE_RAM                                   = 0x24
    WRITE_VCOM_REGISTER                         = 0x2C
    WRITE_LUT_REGISTER                          = 0x32
    SET_DUMMY_LINE_PERIOD                       = 0x3A
    SET_GATE_TIME                               = 0x3B
    BORDER_WAVEFORM_CONTROL                     = 0x3C
    SET_RAM_X_ADDRESS_START_END_POSITION        = 0x44
    SET_RAM_Y_ADDRESS_START_END_POSITION        = 0x45
    SET_RAM_X_ADDRESS_COUNTER                   = 0x4E
    SET_RAM_Y_ADDRESS_COUNTER                   = 0x4F
    TERMINATE_FRAME_READ_WRITE                  = 0xFF

    # valid VCOM values taken from datasheet - change vcom if display looks "grey" happens
    VCOM_VALUES = { "-0.2": 0x0F, "-0.3": 0x14, "-0.4": 0x19, "-0.5": 0x1E, "-0.6": 0x23, "-0.7": 0x28,
                    "-0.8": 0x2D, "-0.9": 0x32, "-1.0": 0x37, "-1": 0x37, "-1.1": 0x3C, "-1.2": 0x41,
                    "-1.3": 0x47, "-1.4": 0x4B, "-1.5": 0x50, "-1.6": 0x55, "-1.7": 0x5A, "-1.8": 0x5F,
                    "-1.9": 0x64, "-2.0": 0x69, "-2": 0x69, "-2.1": 0x6E, "-2.2": 0x73, "-2.3": 0x78,
                    "-2.4": 0x7D, "-2.5": 0x82, "-2.6": 0x87, "-2.7": 0x8C, "-2.8": 0x91, "-2.9": 0x96,
                    "-3.0": 0x9B, "-3": 0x9B, "-3.1": 0xA0, "-3.2": 0xA5, "-3.3": 0xAA}

    # Note from https://www.waveshare.com/wiki/1.54inch_e-Paper_Module#Configuration_of_LUT_table.28SetLut.29
    # LUT - Look-up table is used to set the update mode of the module.This table is provided by us but it may be
    # different* among different batches. If the table changed, we will update the demo code as soon as possible.
    # * in this case this driver needs to be redesigned. simply changed the value is not sufficient.
    model = {
        "1.54": {
            "width": 200,
            "height": 200,
            "update_time": 0.680,  # seconds according to data sheet
            "lut_full_update": [
                0x02, 0x02, 0x01, 0x11, 0x12, 0x12, 0x22, 0x22,
                0x66, 0x69, 0x69, 0x59, 0x58, 0x99, 0x99, 0x88,
                0x00, 0x00, 0x00, 0x00, 0xF8, 0xB4, 0x13, 0x51,
                0x35, 0x51, 0x51, 0x19, 0x01, 0x00
            ],
            "lut_partial_update": [
                0x10, 0x18, 0x18, 0x08, 0x18, 0x18, 0x08, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x13, 0x14, 0x44, 0x12,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            ]
        },
        "2.13": {
            "width": 128,  # real resolution 122 - logic resolution 128
            "height": 250,
            "update_time": 0.680,  # seconds according to data sheet
            "lut_full_update": [
                0x22, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x11,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E,
                0x01, 0x00, 0x00, 0x00, 0x00, 0x00
            ],
            "lut_partial_update": [
                0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x0F, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            ],
        },
        "2.9": {
            "width": 128,
            "height": 296,
            "update_time": 0.600,  # seconds according to data sheet
            "lut_full_update": [
                0x02, 0x02, 0x01, 0x11, 0x12, 0x12, 0x22, 0x22,
                0x66, 0x69, 0x69, 0x59, 0x58, 0x99, 0x99, 0x88,
                0x00, 0x00, 0x00, 0x00, 0xF8, 0xB4, 0x13, 0x51,
                0x35, 0x51, 0x51, 0x19, 0x01, 0x00
            ],
            "lut_partial_update": [
                0x10, 0x18, 0x18, 0x08, 0x18, 0x18, 0x08, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x13, 0x14, 0x44, 0x12,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            ],
        },
    }


class EPaperMQTTMessageConverter(object):
    """Static utility class - converts images and json structures into valid mqtt payloads and back again. To be used
    by sender and driver.

    Additionally, the image is rotated. Thus, it is not necessary that the sender has to know the distribution of the
    x/y-axis or if the display is mounted upside down."""

    @staticmethod
    def _transpose(transpose, image, x, y, display_width, display_height):
        """Rotate the image and adapt the coordinates (upper left corner is 0/0). (0/90/180/270)"""
        image_width, image_height = image.size

        if int(transpose) == 0:
            pass
        elif int(transpose) == 90:
            image = image.transpose(Image.ROTATE_90)
            x, y = y, x
            y = display_height - image_width - y
        elif int(transpose) == 180:
            image = image.transpose(Image.ROTATE_180)
            y = display_height - image_height - y
            x = display_width - image_width - x
        elif int(transpose) == 270:
            image = image.transpose(Image.ROTATE_270)
            x, y = y, x
            x = display_width - image_height - x
        else:
            raise ValueError("Unknown value for transpose: {}. accepted values are 0,90,180,270.".format(transpose))
        return image, x, y

    @staticmethod
    def to_full_image(image):
        """Convert a PIL.Image instance to bytes - the format nedded if the mqtt payload consists of only the image."""
        bytes_image = BytesIO()
        image.save(bytes_image, format="png")
        result = bytes_image.getvalue()
        return result

    @staticmethod
    def from_full_image(msg, transpose, display_width, display_height):
        """Takes bytes and converts them back into an PIL.Image instance (and rotates it). The image is put into a
        json structure."""
        image = Image.open(BytesIO(msg))
        x = 0
        y = 0
        image, x, y = EPaperMQTTMessageConverter._transpose(transpose, image, x, y, display_width, display_height)
        result = [{
            "x": x,
            "y": y,
            "image": image
        }]
        return result

    @staticmethod
    def to_partial_images(image_entry_list):
        """Takes a list containing [x,y,partial images] and converts the images into an utf-8 encoded string that can be
        accepted by mqtt and packs them into a json structure consisting of these string and their x/y values."""
        result = []
        for image_entry in image_entry_list:
            bytes_image = BytesIO()
            image_entry["image"].save(bytes_image, format="png")
            base64_bytes = base64.b64encode(bytes_image.getvalue())
            base64_string = base64_bytes.decode("utf-8")
            entry = {
                "x": int(image_entry["x"]),
                "y": int(image_entry["y"]),
                "image": base64_string
            }
            result.append(entry)
        return json.dumps(result)

    @staticmethod
    def from_partial_images(msg, transpose, display_width, display_height):
        """Takes tha json structure of utf-8 string encoded partial images and their x/y values and converts the
        strings into PIL.Image instances (and rotates them). A json structure with images and x/y is returned.

        The true x-value and width (after transpose) must be multiples of 8. The check cannot be done in
        to_partial_image because the true position is unknown to the sender. Please note that displays that have
        a width that is not a multiple of eight itself have a logic width that satisfy this condition."""

        msg = msg.decode("utf-8")
        result = []
        j = json.loads(msg)
        for image_entry in json.loads(msg):
            image = base64.b64decode(image_entry["image"])
            image = Image.open(BytesIO(image))
            x = int(image_entry["x"])
            y = int(image_entry["y"])
            image, x, y = EPaperMQTTMessageConverter._transpose(transpose, image, x, y, display_width, display_height)
            width, height = image.size
            if x%8 != 0:
                raise ValueError("value for x-axis must be a multiple of 8! ({}%8 != 0)".format(x))
            if width%8 != 0:
                raise ValueError("value for x-size must be a multiple of 8! ({}%8 != 0)".format(width))
            entry = {
                "x": x,
                "y": y,
                "image": image
            }
            result.append(entry)
        return result


class EPaper(ADriver, ASPI, AEvents):
    """Driver for selected e-Papers from Waveshare.

    Currently, three ePapers are supported:
     * 1.54inch https://www.waveshare.com/wiki/1.54inch_e-Paper_Module
     * 2.13inch https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT
     * 2.9inch https://www.waveshare.com/wiki/2.9inch_e-Paper_Module

    This driver basically updates either the whole display (full_image) or selected parts (partial_image). The latter
    one results in faster update times. Internally, the epaper has two buffers. Via a command message the buffers are
    flipped. After flipping, one buffer is used to update the display while the other buffer is ready to receive new
    data via spi. The driver is locked util the display has been fully updated (see
    EPaperMQTTMessageConverter.size[].update_time for additional delay after transmission of data/commands). This
    results in a minimum update frequency of roughly 1 Hz. Nevertheless, the larger the display and the larger the
    updated area an even longer pause between two full image updates is recommended. Tests have shown that full image
    updates on the 2.9" display should have a pause of up to 5* seconds in between. Otherwise the image is grey instead
    of a saturated black. * values may vary heavily.

    When using partial image updates please take the two buffers under consideration. If two different areas are
    updated alternatively, it will result in a "blinking" behavior. The most common case - one static background
    image - and constantly update of the same area can be realised by first sending the full_image_twice and then
    the partial_image messages.

    Partial images must have a width and an x-position value that are multiples of eight. Any other value will result
    in a ValueError. Some displays have a width that is not compliant to this rule. In this case the display will have
    a logic width (e.g. 2.13 inch display has a width of 122 and a logic width of 128).

    The driver entry in the yaml file consists of:
      * ADriver entries
        * topics_sub:
            * full_image - a single image covering the whole display to be placed in the current buffer.
            * full_image_twice - a single image covering the whole display to be placed into both buffers.
            * partial_image - list of image covering only parts of the display plus their position to be placed into
            the current buffer.
            * partial_image_twice - list of image covering only parts of the display plus their position to be placed
            into both buffers.
        * topics_pub:
            * message_queue_size - publishes the number of messages that wait to be processes.
      * ASPI entries
      * EPaper entries
        * size - display-type. one of the keys of EPaperMQTTMessageConverter.size. [1.54, 2.13, 2.9, ...]
        * transpose - 0/90/180/270 rotation applied to all received images.
        * pin_rst - reset gpio pin. according to data sheet
        * pin_dc - data/command pin. flag if value is to be interpreted as command or as data (see data sheet).
        * pin_busy - busy flag. set by epaper (see data sheet).
        * autodeepsleep - if true, epaper is set to deep sleep after each update.
        * VCOM - set vcom supply to given level. (-0.2steps - -3.3 in 0.1V steps; value used in waveform demo is -3.2V)

    Example:
    device:
        type: epaper
        model: 2.13
        spi:
            pin_cs: -1 # use spi cs mechanism. GPIO08/SPI_CE0_N
            bus: 0
            device: 0
            maxspeed: 2000000
        transpose: 90
        pin_rst:  13
        pin_dc:   19
        pin_busy: 6
        autodeepsleep: True
        topics-sub:
            full_image: /display/full_image
            full_image_twice: /display/full_image_twice
            part_image: /display/part_image
            part_image_twice: /display/part_image_twice
        topics-pub:
            message_queue_size: /display/message_queue_size

    Please note that the ePaper drive code is heavily based on the module epd2in13.py implemented by Yehui from
    Waveshare. Methods that are taken from this module are marked with @Waveshare (independently from changes in this
    method done for this module/project).
    """

    _width = -1  # display width
    _height = -1  # display height
    _update_time = -1  # time the epaper needs to update the display to the current buffer
    _not_busy = None  # threading.Event event for the state of the busy pin
    _display_frame_lock = None   # locked during image update (processing time + update_time)
    _lut = None  # lock-up table provided by waveshare
    _lut_full_update = None  # store model s
    _lut_partial_update = None  #
    _auto_deep_sleep = False  # flag is auto deep sleep is enabled
    _transpose = -1  # transpose value
    _busy_pin = -1  # gpio id of busy pin
    _dc_pin = -1  # gpio id of dc pin
    _reset_pin = -1  # gpio id of reset pin
    _vcom = -1  # VCOM driving voltage in hex - must be a value from EPaperConstants.VCOM_VALUES

    _msg_queue_size = 0  # number of mqtt messages that wait to be processed
    _msg_queue = None  # queue with tasks to be executed that are received via mqtt
    _msg_queue_worker_thread = None  # thread that processes all entries that are put to _msg_queue

    def __init__(self, config, verbose, spi_lock = None):
        ADriver.__init__(self, config, verbose)
        AEvents.__init__(self, config, verbose)
        ASPI.__init__(self, config, verbose, spi_lock)

        self._auto_deep_sleep = config["autodeepsleep"]
        self._transpose = config["transpose"]

        self._reset_pin = config["pin_rst"]
        self._dc_pin = config["pin_dc"]
        self._busy_pin = config["pin_busy"]

        self._width = EPaperConstants.model[str(config["model"])]["width"]
        self._height = EPaperConstants.model[str(config["model"])]["height"]
        if self._verbose:
            print("Display set to type {} (w:{}/h:{}).".format(config["model"], self._width, self._height))
        self._update_time = EPaperConstants.model[str(config["model"])]["update_time"]
        self._lut_full_update = EPaperConstants.model[str(config["model"])]["lut_full_update"]
        self._lut_partial_update = EPaperConstants.model[str(config["model"])]["lut_partial_update"]

        self._add_topic_handler(self._topics_sub["full_image"], self._handler_display_full_image)
        self._add_topic_handler(self._topics_sub["full_image_twice"], self._handler_display_full_image_twice)
        self._add_topic_handler(self._topics_sub["part_image"], self._handler_display_part_image)
        self._add_topic_handler(self._topics_sub["part_image_twice"], self._handler_display_part_image_twice)

        try:
            self._vcom = EPaperConstants.VCOM_VALUES[str(config["vcom"])]
        except KeyError:
            raise KeyError("Value for 'vcom' ('{}') must be taken from this list: {}.".
                           format(str(config["vcom"]), EPaperConstants.VCOM_VALUES.keys()))

        self._add_event(self._busy_pin, self._busy_state, 10)
        self._not_busy = threading.Event()
        self._not_busy.set()
        self._display_frame_lock = threading.Lock()

        self._msg_queue = queue.Queue()
        self._msg_queue_size = 0
        self._msg_queue_worker_thread = threading.Thread(target=self._msg_queue_worker)
        self._msg_queue_worker_thread.start()

    def _msg_queue_worker(self):
        """send each item in queue to _display_image, decrease _queue_size and publish new value"""
        while True:
            tasks = self._msg_queue.get()
            if tasks is None:
                break

            for task in tasks:
                self._display_image(task)

            self._msg_queue.task_done()
            self._msg_queue_size = self._msg_queue_size - 1
            if self._verbose:
                print("mqtt message queue size decreased to: {}.".format(self._msg_queue_size))
            self._publish_value(self._topics_pub["message_queue_size"], self._msg_queue_size)

    def _put_to_msg_queue(self, tasks):
        """increase queue size, publish new value and put tasks to _msg_queue"""
        self._msg_queue_size = self._msg_queue_size + 1
        if self._verbose:
            print("mqtt message queue size increased to: {}.".format(self._msg_queue_size))
        self._publish_value(self._topics_pub["message_queue_size"], self._msg_queue_size)
        self._msg_queue.put(tasks)

    def _handler_display_full_image(self, msg):
        """on_message handler for topic sub 'full_image'"""
        if self._verbose:
            print("received full_image in topic {}.".format(type(msg.payload), msg.topic))
        image_entry = EPaperMQTTMessageConverter.from_full_image(msg.payload, self._transpose,
                                                                 self._width, self._height)
        self._put_to_msg_queue((image_entry,))

    def _handler_display_full_image_twice(self, msg):
        """on_message handler for topic sub 'full_image_twice'"""
        if self._verbose:
            print("received full_image_twice in topic {}.".format(type(msg.payload), msg.topic))
        image_entry = EPaperMQTTMessageConverter.from_full_image(msg.payload, self._transpose,
                                                                 self._width, self._height)

        self._put_to_msg_queue((image_entry,image_entry))

    def _handler_display_part_image(self, msg):
        """on_message handler for topic sub 'part_image'"""
        if self._verbose:
            print("received part_image in topic {}.".format(type(msg.payload), msg.topic))
        image_entries = EPaperMQTTMessageConverter.from_partial_images(msg.payload, self._transpose,
                                                                       self._width, self._height)
        self._put_to_msg_queue((image_entries,))

    def _handler_display_part_image_twice(self, msg):
        """on_message handler for topic sub 'part_image_twice'"""
        if self._verbose:
            print("received part_image_twice in topic {}.".format(type(msg.payload), msg.topic))
        image_entries = EPaperMQTTMessageConverter.from_partial_images(msg.payload, self._transpose,
                                                                       self._width, self._height)
        self._put_to_msg_queue((image_entries,image_entries))

    def _busy_state(self, channel):
        """event handler for gpio busy_pin. sets/clears _not_busy Event"""
        if GPIO.input(self._busy_pin) == 1:
            self._not_busy.clear()
        else:
            self._not_busy.set()
        if self._verbose:
            print("edge detected for busy pin ({}). notbusy: {}".format(self._busy_pin, self._not_busy.is_set()))

    def _send_command(self, command):
        """sends a command to the epaper. dc_pin to GPIO.LOW"""
        if self._verbose:
            print(" : send command to epaper")
        GPIO.output(self._dc_pin, GPIO.LOW)
        self._transfer([command])

    def _send_data(self, data):
        """sends data to the epaper. dc_pin to GPIO.HIGH"""
        if self._verbose:
            print(" : send data to epaper")
        GPIO.output(self._dc_pin, GPIO.HIGH)
        self._transfer([data])

    def _init_e_paper(self, full_image):
        """initialize epaper"""
        if self._verbose:
            print("initEPaper")
        # EPD hardware init start
        self._reset()
        self._send_command(EPaperConstants.DRIVER_OUTPUT_CONTROL)
        self._send_data((self._height - 1) & 0xFF)
        self._send_data(((self._height - 1) >> 8) & 0xFF)
        self._send_data(0x00)                     # GD = 0 SM = 0 TB = 0
        self._send_command(EPaperConstants.BOOSTER_SOFT_START_CONTROL)
        self._send_data(0xD7)
        self._send_data(0xD6)
        self._send_data(0x9D)
        self._send_command(EPaperConstants.WRITE_VCOM_REGISTER)
        self._send_data(self._vcom)                     # VCOM 7C
        self._send_command(EPaperConstants.SET_DUMMY_LINE_PERIOD)
        self._send_data(0x1A)                     # 4 dummy lines per gate
        self._send_command(EPaperConstants.SET_GATE_TIME)
        self._send_data(0x08)                     # 2us per line
        self._send_command(EPaperConstants.DATA_ENTRY_MODE_SETTING)
        self._send_data(0x03)                     # X increment Y increment

        if full_image:
            if self._verbose:
                print("set lut to full update")
            self._lut = self._lut_full_update
        else:
            if self._verbose:
                print("set lut to partial update")
            self._lut = self._lut_partial_update

        self._send_lut()
        # EPD hardware init end

    def _reset(self):
        """module reset - often used to awaken the module in deep sleep
        @waveshare"""
        if self._verbose:
            print("reset epaper")
        GPIO.output(self._reset_pin, GPIO.LOW)
        sleep(0.2)
        GPIO.output(self._reset_pin, GPIO.HIGH)
        sleep(0.2)

    def _send_lut(self):
        """set the look-up table register
        @waveshare"""
        if self._verbose:
            print("set lut on paper")
        self._send_command(EPaperConstants.WRITE_LUT_REGISTER)
        # the length of look-up table is 30 bytes
        for i in range(0, len(self._lut)):
            self._send_data(self._lut[i])

    def _get_frame_buffer(self, image):
        """convert an image to a buffer
        @waveshare"""
        if self._verbose:
            print("get frame buffer")
        buf = [0x00] * (self._width * self._height / 8)
        # Set buffer to value of Python Imaging Library image.
        # Image must be in mode 1.
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        if imwidth != self._width or imheight != self._height:
            raise ValueError('Image must be same dimensions as display \
                ({0}x{1}).'.format(self._width, self._height))

        pixels = image_monocolor.load()
        for y in range(self._height):
            for x in range(self._width):
                # Set the bits for the column of pixels at the current position.
                if pixels[x, y] != 0:
                    buf[(x + y * self._width) / 8] |= 0x80 >> (x % 8)
        return buf

    def _set_frame_memory(self, image, x, y):
        """put an image to the frame memory. this won't update the display.
        @waveshare"""
        if self._verbose:
            print("set frame memory")
        if (image == None or x < 0 or y < 0):
            return
        image_monocolor = image.convert('1')
        image_width, image_height = image_monocolor.size
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        x = x & 0xF8
        image_width = image_width & 0xF8
        if (x + image_width >= self._width):
            x_end = self._width - 1
        else:
            x_end = x + image_width - 1
        if (y + image_height >= self._height):
            y_end = self._height - 1
        else:
            y_end = y + image_height - 1
        self._set_memory_area(x, y, x_end, y_end)
        # send the image data
        pixels = image_monocolor.load()
        byte_to_send = 0x00
        for j in range(y, y_end + 1):
            self._set_memory_pointer(x, j)
            self._send_command(EPaperConstants.WRITE_RAM)
            # 1 byte = 8 pixels, steps of i = 8
            for i in range(x, x_end + 1):
                # Set the bits for the column of pixels at the current position.
                if pixels[i - x, j - y] != 0:
                    byte_to_send |= 0x80 >> (i % 8)
                if (i % 8 == 7):
                    self._send_data(byte_to_send)
                    byte_to_send = 0x00

    def _clear_frame_memory(self, color):
        """clear the frame memory with the specified color. this won't update the display.
        @waveshare"""
        if self._verbose:
            print("clear frame memory")
        self._set_memory_area(0, 0, self._width - 1, self._height - 1)
        self._set_memory_pointer(0, 0)
        self._send_command(EPaperConstants.WRITE_RAM)
        # send the color data
        r = int(self._width / 8 * self._height)
        for i in range(0, r):
            self._send_data(color)

    def _display_frame(self):
        """update the display
        there are 2 memory areas embedded in the e-paper display but once this function is called, the the next
        action of SetFrameMemory or ClearFrame will set the other memory area.
        @waveshare"""
        if self._verbose:
            print("display frame")
        self._send_command(EPaperConstants.DISPLAY_UPDATE_CONTROL_2)
        self._send_data(0xC4)
        self._send_command(EPaperConstants.MASTER_ACTIVATION)
        self._send_command(EPaperConstants.TERMINATE_FRAME_READ_WRITE)
        self._wait_until_idle()

    def _set_memory_area(self, x_start, y_start, x_end, y_end):
        """specify the memory area for data R/W
        @waveshare"""
        if self._verbose:
            print("set memory area.")
        self._send_command(EPaperConstants.SET_RAM_X_ADDRESS_START_END_POSITION)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self._send_data((x_start >> 3) & 0xFF)
        self._send_data((x_end >> 3) & 0xFF)
        self._send_command(EPaperConstants.SET_RAM_Y_ADDRESS_START_END_POSITION)
        self._send_data(y_start & 0xFF)
        self._send_data((y_start >> 8) & 0xFF)
        self._send_data(y_end & 0xFF)
        self._send_data((y_end >> 8) & 0xFF)

    def _set_memory_pointer(self, x, y):
        """specify the start point for data R/W
        @waveshare"""
        if self._verbose:
            print("set memory pointer")
        self._send_command(EPaperConstants.SET_RAM_X_ADDRESS_COUNTER)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self._send_data((x >> 3) & 0xFF)
        self._send_command(EPaperConstants.SET_RAM_Y_ADDRESS_COUNTER)
        self._send_data(y & 0xFF)
        self._send_data((y >> 8) & 0xFF)
        self._wait_until_idle()

    def _deep_sleep(self):
        """After this command is transmitted, the chip would enter the deep-sleep mode to save power. The deep sleep
        mode would return to standby by hardware reset. You can use reset() to awaken or init() to initialize.
        @waveshare"""
        if self._verbose:
            print("activate deep sleep")
        self._send_command(EPaperConstants.DEEP_SLEEP_MODE)
        self._wait_until_idle()

    def _display_image(self, images):
        """send received image(s) to the epaper.

        acquire the lock (_display_frame_lock), wake up from deep sleep (optional), put all (partial) images into the current frame buffer,
        display frame, send back to deep sleep (optional), wait the _update_time and then release the lock."""
        if self._verbose:
            print("display image")
        with self._display_frame_lock:
            if self._verbose:
                print("... lock acquired")
            if self._auto_deep_sleep:
                self._reset()

            for map in images:
                x = map["x"]
                y = map["y"]
                image = map["image"]
                if self._verbose:
                    print("... added image at {}/{}.".format(x,y))
                self._set_frame_memory(image, x, y)

            self._display_frame()
            if self._auto_deep_sleep:
                self._deep_sleep()
            sleep(self._update_time)
            if self._verbose:
                print("... image displayed. lock released.")

    def _wait_until_idle(self):
        """wait until the epaper releases the busy flag."""
        if self._verbose:
            print("wait_until_idle")
        self._not_busy.wait()

    def _start_sequence(self):
        """@ADriver._start_sequence"""
        if self._verbose:
            print("start device '{}.{}'.".format(self._type, self._name))

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._reset_pin, GPIO.OUT)
        GPIO.setup(self._dc_pin, GPIO.OUT)
        GPIO.setup(self._busy_pin, GPIO.IN)

        self._register_events()
        self._connect_spi()
        self._init_e_paper(False)
        self._subscribe_topics()

    def _stop_sequence(self):
        """@ADriver._stop_sequence"""
        if self._verbose:
            print("stop device '{}.{}'.".format(self._type, self._name))

        with self._display_frame_lock:
            self._unsubscribe_topics()
            self._deep_sleep()
            self._unregister_events()
            self._disconnect_spi()

            GPIO.cleanup(self._reset_pin)
            GPIO.cleanup(self._dc_pin)
            GPIO.cleanup(self._busy_pin)


def standalone():
    """Calls the static method EPaper.standalone()."""
    EPaper.standalone()


if __name__ == "__main__":
    EPaper.standalone()
