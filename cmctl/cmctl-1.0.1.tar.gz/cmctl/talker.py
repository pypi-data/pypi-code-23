'''Device talker module.'''

import os
import sys
import time
import serial

class TalkerException(Exception):
    '''Generic communication error exception.'''
    pass

class Talker:
    '''Class providing communication with device.'''

    def __init__(self, device):
        '''Open device and flush buffers.'''
        exclusive = False if os.name == 'nt' or sys.platform == 'win32' else True
        self._ser = serial.Serial(device, baudrate=9600, timeout=3, exclusive=exclusive)
        time.sleep(0.5)
        self._ser.flush()
        self._ser.write(b'\x1b')

    def command(self, command):
        '''Execute command on device.'''
        command += '\r\n'
        self._ser.write(command.encode('ascii'))
        status = self._ser.readline().decode('ascii').rstrip()
        if not status or status != 'OK':
            raise TalkerException

    def query(self, query):
        '''Execute query on device (command with expected response).'''
        query += '\r\n'
        self._ser.write(query.encode('ascii'))
        result = self._ser.readline().decode('ascii').rstrip()
        if not result:
            raise TalkerException
        status = self._ser.readline().decode('ascii').rstrip()
        if not status or status != 'OK':
            raise TalkerException
        return result
