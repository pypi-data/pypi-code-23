import subprocess
import os
import select
import time
from xboxcontroller.error import XboxError


class Joystick:

    def __init__(self, refresh_rate=30):
        try:
            self.proc = subprocess.Popen(['xboxdrv', '--no-uinput', '--detach-kernel-driver'], stdout=subprocess.PIPE)
            self.pipe = self.proc.stdout

        except FileNotFoundError:
            raise XboxError('No Xbox Controller Driver found -- Please install it with sudo apt-get install xboxdrv')

        self.connectStatus = False
        self.reading = '0' * 140

        self.refreshTime = 0
        self.refreshDelay = 1.0 / refresh_rate

        found = False
        wait_time = time.time() + 2
        while wait_time > time.time() and not found:
            readable, writeable, exception = select.select([self.pipe], [], [], 0)
            if readable:
                response = self.pipe.readline()
                if response[0:7] == 'No Xbox':
                    raise XboxError('No Xbox controller/receiver found')
                if response[0:12] == 'Press Ctrl-c':
                    found = True
                if len(response) == 140:
                    found = True
                    self.connectStatus = True
                    self.reading = response

        if not found:
            self.close()
            raise XboxError('Unable to detect Xbox controller/receiver - Run python as sudo')

    def refresh(self):
        response = None
        if self.refreshTime < time.time():
            self.refreshTime = time.time() + self.refreshDelay
            readable, writeable, exception = select.select([self.pipe], [], [], 0)
            if readable:
                while readable:
                    response = self.pipe.readline()
                    if len(response) == 0:
                        raise IOError('Xbox controller disconnected from USB')
                    readable, writeable, exception = select.select([self.pipe], [], [], 0)

                if len(response) == 140:
                    self.connectStatus = True
                    self.reading = response
                else:
                    self.connectStatus = False

    def connected(self):
        self.refresh()
        return self.connectStatus

    def left_x(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[3:9])
        return self.axis_scale(raw, deadzone)

    def left_y(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[13:19])
        return self.axis_scale(raw, deadzone)

    def right_x(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[24:30])
        return self.axis_scale(raw, deadzone)

    def right_y(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[34:40])
        return self.axis_scale(raw, deadzone)

    def dpad_up(self):
        self.refresh()
        return int(self.reading[45:46])

    def dpad_down(self):
        self.refresh()
        return int(self.reading[50:51])

    def dpad_left(self):
        self.refresh()
        return int(self.reading[55:56])

    def dpad_right(self):
        self.refresh()
        return int(self.reading[60:61])

    def back(self):
        self.refresh()
        return int(self.reading[68:69])

    def guide(self):
        self.refresh()
        return int(self.reading[76:77])

    def start(self):
        self.refresh()
        return int(self.reading[84:85])

    def left_thumbstick(self):
        self.refresh()
        return int(self.reading[90:91])

    def right_thumbstick(self):
        self.refresh()
        return int(self.reading[95:96])

    def a(self):
        self.refresh()
        return int(self.reading[100:101])

    def b(self):
        self.refresh()
        return int(self.reading[104:105])

    def x(self):
        self.refresh()
        return int(self.reading[108:109])

    def y(self):
        self.refresh()
        return int(self.reading[112:113])

    def left_bumper(self):
        self.refresh()
        return int(self.reading[118:119])

    def right_bumper(self):
        self.refresh()
        return int(self.reading[123:124])

    def left_trigger(self):
        self.refresh()
        return int(self.reading[129:132]) / 255.0

    def right_trigger(self):
        self.refresh()
        return int(self.reading[136:139]) / 255.0

    def left_stick(self, deadzone=4000):
        self.refresh()
        return self.left_x(deadzone), self.left_y(deadzone)

    def right_stick(self, deadzone=4000):
        self.refresh()
        return self.right_x(deadzone), self.right_y(deadzone)

    @staticmethod
    def axis_scale(raw, deadzone):
        if abs(raw) < deadzone:
            return 0.0
        else:
            if raw < 0:
                return (raw + deadzone) / (32768.0 - deadzone)
            else:
                return (raw - deadzone) / (32767.0 - deadzone)

    @staticmethod
    def close():
        os.system('pkill xboxdrv')
