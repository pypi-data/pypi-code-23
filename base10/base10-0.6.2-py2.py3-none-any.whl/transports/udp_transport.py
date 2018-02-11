from socket import socket, AF_INET, SOCK_DGRAM

from base10.base import Writer
from base10.exceptions import TransportError


class UDPWriter(Writer):
    def __init__(self, host, port):
        self._host = host
        self._port = port

        self._socket = socket(AF_INET, SOCK_DGRAM)

    def write(self, string):
        self._socket.sendto(string + '\n', (self._host, self._port))
