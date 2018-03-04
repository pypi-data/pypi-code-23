import socket
import struct
from typing import Union

default_port = 56778
base_address = 4009754625
max_channel = 16777215
max_payload = 500
max_packet = max_payload + 8
magic = b'\x4d\x54\x4c\x4b'  # MTLK


def channel_address(channel: int) -> int:
    return (channel % max_channel) + base_address


class Writer:
    """
    Socket wrapper for sending message over UDP multicast. Instances supports context-manager
    """

    def __init__(self):
        self.__closed = False
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def write(self, channel: int, payload: Union[str, bytes]):
        """
        Make packet and send message as UDP multicast message
        :param channel: any number
        :param payload: up to 500 bytes (or string) message. Bigger messages will be cut
        """
        addr = channel_address(channel)
        if isinstance(payload, str):
            payload = payload.encode()
        if len(payload) > max_payload:
            payload = payload[:max_payload]
        data = struct.pack('!4sI' + str(len(payload)) + 's', magic, channel, payload)
        addr_bs = struct.pack('!I', addr)
        to = (socket.inet_ntoa(addr_bs), default_port)
        self.__socket.sendto(data, to)

    def close(self):
        """
        Close socket. Can be called mutliple times. Better to use context manager
        """
        if not self.__closed:
            self.__socket.close()
            self.__closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


class Packet:
    """
    Container for received message. Channel - integer, payload - bytes
    """

    def __init__(self, channel: int, payload: bytes):
        self.channel = channel  # type: int
        self.payload = payload  # type: bytes


class Reader:
    """
    Wrapper over UDP socket for reading packets
    """

    def __init__(self, timeout: float = None):
        """
        Create and bind UDP socket. If timeout is not none - setup socket operation timeout
        :param timeout: float or None
        """
        self.__closed = False
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        if timeout is not None:
            timeout = float(timeout)
        try:
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind(('0.0.0.0', default_port))
            if timeout is not None:
                self.__socket.settimeout(timeout)
        except SystemError:
            self.__socket.close()
            raise
        self.__channels = set()

    def subscribe(self, *channels: int):
        """
        Subscribe to specified channels
        :param channels: numbers
        """
        for channel in channels:
            if channel in self.__channels:
                continue
            address = channel_address(channel)
            mreq = struct.pack('!IL', address, socket.INADDR_ANY)
            self.__socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            self.__channels.add(channel)

    def unsubscribe(self, *channels: int):
        """
        Unsubscribe from specified channels
        :param channels: numbers
        """
        for channel in channels:
            if channel not in self.__channels:
                continue
            address = channel_address(channel)
            mreq = struct.pack('!IL', address, socket.INADDR_ANY)
            self.__socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            self.__channels.remove(channel)

    def read(self) -> Packet:
        """
        Read messages from socket. Silently drops unmatched or wrong messages
        :return: Packet
        """
        while True:
            data = self.__socket.recv(max_packet)
            if len(data) < 8:  # cheap validation
                continue
            try:
                cookie, channel, payload = struct.unpack('!4sI' + str(len(data) - 8) + 's', data)
            except struct.error:
                continue

            if cookie != magic:
                continue
            if channel not in self.__channels:
                continue
            return Packet(channel, payload)

    def close(self):
        """
        Close socket. Can be called mutliple times. Better to use context manager
        """
        if not self.__closed:
            self.__socket.close()
            self.__closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
