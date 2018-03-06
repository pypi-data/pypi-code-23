"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
import os
import os.path
import array
from time import sleep
from threading import Thread, Lock
import select
import fcntl
import sys
import errno

from .common import TimeoutException


class WrongStateError(Exception):
    pass


class JemuUart(object):
    """
    Represents a UART device.
    """
    _uart_device = None
    _uart_device_path = None

    def __init__(self, uart_device_path, vlab):
        self._uart_device = None
        self._uart_device_fd = None
        self._uart_device_path = uart_device_path
        self._buffer = b''
        self._vlab = vlab
        self._read_from_uart_thread = None
        self._lock = Lock()
        self._print_to_screen = False
        self._should_close_thread = False
        try:
            os.unlink(uart_device_path)
        except:
            pass

    def print_uart_to_screen(self):
        self._print_to_screen = True

    def remove(self):
        if not os.path.exists(self._uart_device_path):
            return

        if not os.path.islink(self._uart_device_path):
            raise Exception(self._uart_device_path + ' not symbolic link')

        os.unlink(self._uart_device_path)

    def open(self):
        if not os.path.islink(self._uart_device_path):
            raise Exception(self._uart_device_path +
                            ' not found or not symbolic link')

        self._uart_device = open(self._uart_device_path, "w+")
        self._uart_device_fd = self._uart_device.fileno()
        flag = fcntl.fcntl(self._uart_device_fd, fcntl.F_GETFL)
        fcntl.fcntl(self._uart_device_fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)
        self._read_from_uart_thread = Thread(target=self._read_from_uart)
        self._read_from_uart_thread.start()

    def _read_from_uart(self):
        new_data = ''
        while not self._should_close_thread:
            try:
                readable, writable, exceptional = select.select([self._uart_device_fd], [], [self._uart_device_fd], 0.3)
            except select.error as e:
                if self._should_close_thread:
                    break
                else:
                    raise IOError('Uart device was closed unexpectadly')
            if self._should_close_thread:
                break
            if self._uart_device_fd in readable:

                new_data = self._uart_device.read(1024)
                if new_data == '':
                    break
                with self._lock:
                    self._buffer += new_data
            elif self._uart_device_fd in exceptional:
                raise IOError('uart device was closed unexpectedly')
            if self._print_to_screen:
                sys.stdout.write(new_data)

    def close(self):
        self._should_close_thread = True
        if self._uart_device:
            if self._read_from_uart_thread.is_alive():
                self._read_from_uart_thread.join()
            self._uart_device.close()

    def read_line(self, line_separator=b'\r\n'):
        """
        Reads a single line from UART.

        :param line_separator: Substring for separating lines. Usually b'\\\\r\\\\n' or b'\\\\n'

        :return: A byte string of data read from the device, including line_separator
        """
        while line_separator not in self._buffer:
            sleep(0.2)
        with self._lock:
            line_length = self._buffer.find(line_separator) + len(line_separator)
            data = self._buffer[:line_length]
            self._buffer = self._buffer[line_length:]
        return data

    def read(self):
        """

        :return: data available on the UART device. Returns an empty bytes string if no data is available.
        """
        with self._lock:
            data = self._buffer
            self._buffer = b''
        return data

    def wait_until_uart_receives(self, data, timeout=None):
        """
        Blocks until specified data is received on UART.
        If the device is paused, this function will continue the execution and will pause the device when the data is ready or timeout occured.
        If the device is running, the function will not pause the device.

        :param data: Expected bytes string.
        :param timeout: Emulation time specified in milliseconds. jumper.vlab.TimeoutException is raised if timeout occurred before data was available in the buffer.
        :return: The data available on in the UART buffer when the specified data was received. Note that this can be more than the data provided in the data parameter.
        """
        original_state = self._vlab.get_state()

        if original_state == 'running':
            self._vlab.pause()
        elif original_state != 'paused':
            raise WrongStateError('state should be paused or running but was {}'.format(original_state))

        if timeout is not None:
            self._vlab.stop_after_ms(timeout)

        self._vlab.resume()

        while data not in self._buffer and self._vlab.get_state() == 'running':
            sleep(0.2)

        if timeout is not None:
            self._vlab.cancel_stop()

        if original_state == 'running':
            self._vlab.resume()
        elif original_state == 'paused':
            self._vlab.pause()
        with self._lock:
            if data in self._buffer:
                tmp = self._buffer
                self._buffer = b''
                return tmp

        raise TimeoutException("timeout while waiting for data from uart")

    def write(self, data):
        """
        Writes data to UART

        :param data: Data to write
        """
        self._uart_device.write(data)
