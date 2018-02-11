import sys
from socket import socket, AF_INET, SOCK_DGRAM

from base10.base import Writer
from base10.exceptions import TransportError

PY3 = sys.version_info.major == 3


class UDPWriter(Writer):
    def __init__(self, host, port):
        self._host = host
        self._port = port

        self._socket = socket(AF_INET, SOCK_DGRAM)

    def write(self, string):
        if PY3:
            self._socket.sendto(
                string.encode('utf8') + b'\n', (self._host, self._port)
            )
        else:
            self._socket.sendto(string + '\n', (self._host, self._port))
