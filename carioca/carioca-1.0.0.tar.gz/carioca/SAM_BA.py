#
# The MIT License (MIT)
#
# Copyright (c) 2016, 2018 eGauge Systems LLC
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Unfortunately, the behavior of SAM-BA depends on the processor/version.
#
# On SAM9G20, the version is reported as:
#
#	v1.5 Mar 12 2008 16:13:23
#
# Whereas on SAMA5D2, it's reported as:
#
#	v1.2 Dec  1 2015 09:20:36
#
# Note that the date here is much newer, yet the version number is lower.
#
# The older SAM-BA behaves roughtly like this:
#
#  Text mode:
#	Each reply ends with '\n\r>'.  The very first reply *may* start
#	with '>'.  This is because SAM-BA may not initially know where
#	to send the prompt to (the USB interface or the serial debug port).
#
#  Binary mode:
#	There is neither a start nor a stop marker (which makes it impossible
#	to tell the end of the "V#" command).
#
# The newer SAM-BA behaves roughly like this:
#
#  Text mode:
#	Each reply starts with '\n\r' and ends with '\n\r>'.
#  Binary mode:
#	Each reply ends with '\n\r' (there is no start sequence).
#
# Due to the complicated differences in text mode, we only support binary mode.
#
# Commands:
#
#  O<addr>,<val>#	- write a byte
#  o<addr>,#		- read a byte
#  H<addr>,<val>#	- write a half word (16 bits)
#  h<addr>,#		- read a half world
#  W<addr>,<val>#	- write a word (32 bits)
#  w<addr>,#		- read a word
#  S<addr>,[<size>]#	- send a file (<size> only needed in non-XMODEM mode)
#  R<addr>,<size>#	- receive a file
#  G<addr>#		- go
#  V#			- display version
#
import struct

from xmodem import XMODEM

# Atmel documentation doesn't make this very clear, but the XMODEM
# protocol is used only on the UART/DBGU port.  When communicating
# over the USB device port, the raw data is directly exchanged with
# the port.
USE_XMODEM = True

class Error(Exception):
    pass

class Monitor:

    @staticmethod
    def size_to_code(size):
        if size == 1:
            cmd = 'o'
        elif size == 2:
            cmd = 'h'
        elif size == 4:
            cmd = 'w'
        else:
            raise Error('Unsupported size', size)
        return cmd

    def __init__(self, serial_interface):
        self.serial = serial_interface
        # force binary mode
        self.serial.write('N#'.encode('utf-8'))

    def _xmodem_getc(self, size, timeout=1):
        saved_timeout = self.serial.timeout
        self.serial.timeout = timeout
        val = self.serial.read(size)
        self.serial.timeout = saved_timeout
        return val

    def _xmodem_putc(self, data, timeout=1):
        saved_timeout = self.serial.timeout
        self.serial.write_timeout = timeout
        val = self.serial.write(data)
        self.serial.write_timeout = saved_timeout
        return val

    def _read_line(self):
        data = bytes()
        eol = '\n\r'.encode('utf-8')
        saved_timeout = self.serial.timeout
        self.serial.timeout = 0.1
        while True:
            ret = self.serial.read(1)
            if len(ret) == 0:
                break		# timed out
            data += ret
            if len(data) >= len(eol) and data[len(data) - len(eol):] == eol:
                if len(data) == len(eol):
                    # SAM-BA may issue a \n\r after "N#"...
                    data = bytes()
                else:
                    data = data[0:len(data) - len(eol)]
                    break
        self.serial.timeout = saved_timeout
        return data.decode('utf-8')

    def version(self):
        self.serial.write('V#'.encode('utf-8'))
        reply = self._read_line()
        if len(reply) == 0:
            raise Error('Unable to read SAM-BA version')
        return reply

    def write(self, addr, value, size):
        cmd = self.size_to_code(size).upper()
        self.serial.write(('%c%x,%x#' % (cmd, addr, value)).encode('utf-8'))

    def write_byte(self, addr, value):
        self.write(addr, value, size=1)

    def write_halfword(self, addr, value):
        self.write(addr, value, size=2)

    def write_word(self, addr, value):
        self.write(addr, value, size=4)

    def read(self, addr, size):
        cmd = self.size_to_code(size).lower()
        self.serial.write(('%c%x,#' % (cmd, addr)).encode('utf-8'))
        code = 'BHHI'[size - 1]
        ret = self.serial.read(size)
        ret = struct.unpack('<%c' % code, ret)[0]
        return ret

    def read_byte(self, addr):
        return self.read(addr, 1)

    def read_halfword(self, addr):
        return self.read(addr, 2)

    def read_word(self, addr):
        return self.read(addr, 4)

    def send_file(self, addr, stream):
        if USE_XMODEM:
            self.serial.write(('S%x,#' % addr).encode('utf-8'))
            prot = XMODEM(self._xmodem_getc, self._xmodem_putc)
            prot.send(stream)
        else:
            data = stream.read()
            self.serial.write(('S%x,%x#' % (addr, len(data))).encode('utf-8'))
            self.serial.write(data)

    def receive_file(self, addr, size, stream):
        self.serial.write(('R%x,%x#' % (addr, size)).encode('utf-8'))
        if USE_XMODEM:
            prot = XMODEM(self._xmodem_getc, self._xmodem_putc)
            prot.recv(stream, delay=0)
        else:
            stream.write(self.serial.read(size))

    def go(self, addr):
        self.serial.write(('G%x#' % addr).encode('utf-8'))
