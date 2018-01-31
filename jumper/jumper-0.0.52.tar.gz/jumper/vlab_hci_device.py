from __future__ import print_function

import os
import errno
import subprocess
from time import sleep
import re
import warnings

import timeout_decorator


class BluezError(Exception):
    pass


class VirtualHciDevice(object):
    _hci_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), "hci")
    _hci_executable = os.path.join(_hci_directory, "hci")
    _uart_file = os.path.join(_hci_directory, "uart")

    def __init__(self):
        self._hci_process = None
        self._btattach_process = None
        self._btmon_process = None
        self._device_index = None

    @staticmethod
    def _check_version():
        try:
            btattach_version_process = subprocess.Popen(['btattach', '--version'], stdout=subprocess.PIPE)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise BluezError("btattach not found, could not connect virtual hci device. Please make sure you have Bluez 5.45 or higher installed")
            else:
                raise e

        btattach_version_process.wait()
        stdout, stderr = btattach_version_process.communicate()
        version = stdout.split('.')
        if int(version[0]) < 5 or (int(version[0]) == 5 and int(version[1]) < 45):
            warnings.warn(
                'Old version of Bluez found, virtual HCI should be used with Bluez version >= 5.45, other versions might behave unexpectedly'
            )

    @property
    def device_name(self):
        return 'hci{}'.format(self._device_index) if self._device_index else None

    def start(self):
        try:
            os.remove(self._uart_file)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise e

        self._check_version()
        self._btmon_process = subprocess.Popen(['btmon'])
        sleep(0.5)
        self._hci_process = subprocess.Popen([self._hci_executable], cwd=self._hci_directory)
        sleep(1)
        self._btattach_process = subprocess.Popen(
            ['btattach', '-S', '115200', '-B', self._uart_file, '-P', 'h4'],
            # stdout=subprocess.PIPE
        )

        @timeout_decorator.timeout(5)
        def wait_for_device_index(btattach_process):
            sleep(0.5)
            self._device_index = '0'
            # TODO: find correct deice_index
            # regex = r'Device index ([0-9]+?) attached'
            # while True:
            #     line = btattach_process.stdout.readline()
            #     if re.match(regex, line):
            #         self._device_index = re.search(regex, line).group(1)
            #         return

        try:
            wait_for_device_index(self._btattach_process)
        except timeout_decorator.TimeoutError:
            self.stop()
            raise BluezError("btattach timed out")

        try:
            subprocess.check_call(['hciconfig', self.device_name, 'up'])
        except subprocess.CalledProcessError:
            self.stop()
            raise

    def stop(self):
        for process in [self._btattach_process, self._hci_process, self._btmon_process]:
            if process:
                if process.poll() is None:
                    process.terminate()
                    process.wait()
