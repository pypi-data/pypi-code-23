import socket
import json
import time
from enum import IntEnum

from fondue import FondueError

HEADER = b'OPN'


# Enum containing packet codes
class Packet(IntEnum):
    GETEXTIP = 0x57
    SENDEXTIP = 0x58
    PEER = 0x59
    PEERCONFIRM = 0x60
    TIMING = 0x61
    KEEPALIVE = 0x62
    DATA = 0x63


class PacketError(FondueError):
    pass


# Parses a packet into type and data
def parse_packet(b):
    if len(b) < 4:
        raise PacketError('Invalid packet length')
    if b[:3] != HEADER:
        raise PacketError('Invalid packet header')
    if b[3] not in [item.value for item in Packet]:
        raise PacketError('Invalid packet type')
    return {'type': b[3], 'data': b[4:]}


class DummySocket:
    def __init__(self, addr):
        self.addr = addr
        self.ip, self.port = self.addr
        self.buffer = []
        self.offset = 0
        self.lookup = {}

    def close(self):
        self.buffer = []

    def write_into_buffer(self, src_ip, src_port, data, buffer):
        packet = json.dumps({'src_ip': src_ip, 'src_port': src_port, 'data': list(data)})
        buffer.append(packet)

    def register(self, addr, buffer):
        self.lookup[addr] = buffer

    def sendto(self, b, addr):
        if addr in self.lookup:
            self.write_into_buffer(self.ip, self.port, b, self.lookup[addr])

    def recvfrom(self, size):
        start = time.time()
        while True:
            if len(self.buffer) != 0:
                packet = json.loads(self.buffer.pop(0))
                break
            time.sleep(0)
            if time.time()-start > 0.1:
                raise socket.timeout
        packet['data'] = bytes(packet['data'])
        return packet['data'], (packet['src_ip'], packet['src_port'])


class NATSocket(DummySocket):
    def __init__(self, priv_addr, pub_addr):
        DummySocket.__init__(self, priv_addr)
        self.pub_ip, self.pub_port = pub_addr
        self.allowed = []

    def sendto(self, b, addr):
        if addr in self.lookup:
            self.write_into_buffer(self.pub_ip, self.pub_port, b, self.lookup[addr])
        self.allowed.append(addr)

    def recvfrom(self, size):
        start = time.time()
        while True:
            if len(self.buffer) != 0:
                packet = json.loads(self.buffer.pop(0))
                addr = (packet['src_ip'], packet['src_port'])
                if addr in self.allowed:
                    break
                else:
                    print('Packet from', addr, 'blocked by NAT')
            time.sleep(0)
            if time.time() - start > 0.5:
                raise socket.timeout
        packet['data'] = bytes(packet['data'])
        return packet['data'], (packet['src_ip'], packet['src_port'])





