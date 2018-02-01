"""
 Copyright (c) 2017 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

 Last modified 07 December 2017
"""

from microbit import *


# This is a script used to control a micro:bit from s2m

# This loop continuously polls the sensors and then prints a reply string.
# It also continuously calls readline to check for commands.
# A command is specified as comma delimited string with the command
# as the first element followed by its parameters.

# Commands:
#   d - display the specified image
#   s - scroll the specified text
#   p - control a pixel for the specified row, column and intensity
#   c - clear the display (no parameters)
#   a - analog write for the specified pin and value (range 0-1023)
#   t - digital write for the specified pin and value (0 or 1)
#   v - get version string

class S2M:
    def __init__(self):
        self.image_dict = {"HAPPY": Image.HAPPY, "SAD": Image.SAD, "ANGRY": Image.ANGRY, "SMILE": Image.SMILE,
                           "CONFUSED": Image.CONFUSED, "ASLEEP": Image.ASLEEP, "SURPRISED": Image.SURPRISED,
                           "SILLY": Image.SILLY, "FABULOUS": Image.FABULOUS, "MEH": Image.MEH, "YES": Image.YES,
                           "NO": Image.NO, "RABBIT": Image.RABBIT, "COW": Image.COW, "ROLLERSKATE": Image.ROLLERSKATE,
                           "HOUSE": Image.HOUSE, "SNAKE": Image.SNAKE, "HEART": Image.HEART, "DIAMOND": Image.DIAMOND,
                           "DIAMOND_SMALL": Image.DIAMOND_SMALL, "SQUARE": Image.SQUARE,
                           "SQUARE_SMALL": Image.SQUARE_SMALL, "TRIANGLE": Image.TRIANGLE,
                           "TARGET": Image.TARGET, "STICKFIGURE": Image.STICKFIGURE,
                           "ARROW_N": Image.ARROW_N, "ARROW_NE": Image.ARROW_NE, "ARROW_E": Image.ARROW_E,
                           "ARROW_SE": Image.ARROW_SE, "ARROW_S": Image.ARROW_S, "ARROW_SW": Image.ARROW_SW,
                           "ARROW_W": Image.ARROW_W, "ARROW_NW": Image.ARROW_NW}

        self.command_dispatch = {'d': self.display_image, 's': self.scroll, 'p': self.write_pixel,
                                 'c': self.display_clear, 'a': self.analog_write, 't': self.digital_write,
                                 'g': self.poll, 'v': self.get_version, 'z': self.get_accel_values,
                                 'b': self.get_button_a, 'e': self.get_button_b }

        self.sensor_string = ""

        while True:
            data = uart.readline()
            sleep(8)
            if data:
                cmd = str(data, 'utf-8').rstrip()
            if not len(cmd):
                continue
            self.cmd_list = cmd.split(",")
            # get command id

            try:
                cmd_id = self.cmd_list[0]
            except IndexError:
                continue
            if cmd_id in self.command_dispatch:
                self.command_dispatch[cmd_id]()

    def display_image(self):
        try:
            image_key = self.cmd_list[1]
        except IndexError:
            return
        if image_key in self.image_dict:
            display.show(self.image_dict.get(image_key), wait=False)

    def scroll(self):
        display.scroll(str(self.cmd_list[1]), wait=False)

    def write_pixel(self):

        try:
            x = int(self.cmd_list[1])
        except ValueError:
            return
        except IndexError:
            return

        if x < 0:
            x = 0
        if x > 4:
            x = 4

        try:
            y = int(self.cmd_list[2])
        except ValueError:
            return
        except IndexError:
            return

        if y < 0:
            y = 0
        if y > 4:
            y = 4
        try:
            value = int(self.cmd_list[3])
        except ValueError:
            return
        except IndexError:
            return

        if value < 0:
            value = 0
        if value > 9:
            value = 9
        display.set_pixel(x, y, value)

    def display_clear(self):
        display.clear()

    def analog_write(self):
        # if values are out of range, command is ignored

        # check pin and value ranges
        try:
            pin = int(self.cmd_list[1])
            value = int(self.cmd_list[2])
        except IndexError:
            return
        except ValueError:
            return

        if 0 <= pin <= 2:
            if not 0 <= value <= 1023:
                value = 256
            if pin == 0:
                pin0.write_analog(value)
            elif pin == 1:
                pin1.write_analog(value)
            elif pin == 2:
                pin2.write_analog(value)

    def digital_write(self):
        # digital write command
        # check pin and value ranges
        # if values are out of range, command is ignored
        try:
            pin = int(self.cmd_list[1])
            value = int(self.cmd_list[2])
        except IndexError:
            return
        except ValueError:
            return

        if 0 <= pin <= 2:
            if 0 <= value <= 1:
                if pin == 0:
                    pin0.write_digital(value)
                elif pin == 1:
                    pin1.write_digital(value)
                elif pin == 2:
                    pin2.write_digital(value)
            else:
                pass

    def poll(self):
        # This string will contain the sensor values and will
        # be "printed" to the serial port.
        # Fields are comma delimited
        self.sensor_string = ""

        # accelerometer
        self.get_accel_values(poll=True)

        # buttons
        self.get_button_a(poll=True)
        self.get_button_b(poll=True)

        # get digital input pin values
        # sensor_string += str(pin0.read_digital()) + ','
        #
        # sensor_string += str(pin1.read_digital()) + ','
        #
        # sensor_string += str(pin2.read_digital()) + ','
        #
        # # get analog input pin values
        # sensor_string += str(pin0.read_analog()) + ','
        #
        # sensor_string += str(pin1.read_analog()) + ','
        #
        # sensor_string += str(pin2.read_analog())

        print(self.sensor_string)

    def get_version(self):
        print('s2mb.py Version 1.06 07 December 2017')

    def get_accel_values(self, poll=False):
        xyz = accelerometer.get_values()
        try:
            x = xyz[0]
            y = xyz[1]
            z = xyz[2]
        except IndexError:
            return
        values = str(x) + ',' + str(y) + ',' + str(z) + ','
        if poll:
            self.sensor_string += values
        else:
            print(values)

    def get_button_a(self, poll=False):
        value = str(button_a.is_pressed()) + ','
        if poll:
            self.sensor_string += value
        else:
            print(value)

    def get_button_b(self, poll=False):
        value = str(button_b.is_pressed()) + ','
        if poll:
            self.sensor_string += value
        else:
            print(value)