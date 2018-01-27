#!/usr/bin/env python3
import os
import sys
import struct
import socket
import subprocess
from fcntl import ioctl
from threading import Thread

from fondue.packets import Packet

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000
SIOCSIFADDR = 0x8916


def parse(frame):
    if frame[0] == Packet.KEEPALIVE:  # Keepalive packet, not an ethernet frame
        return None, 'KEEPALIVE'
    elif frame[0] != Packet.DATA:  # Only process data packets
        return None
    if frame[13] != 0x08:  # Support only ARP and IP
        return None
    if frame[14] == 0x06:  # ARP
        # Begin at offset 16
        if frame[16] != 1:  # Only support Ethernet hardware type
            return None
        elif frame[17] != 0x08 or frame[18] != 0x00:  # Only support IP over ARP
            return None
        data = {'src': ':'.join('%02x' % b for b in frame[7:13]), 'dst': ':'.join('%02x' % b for b in frame[1:7]),
                'src_ip': ip_to_str(frame[29:33]), 'dst_ip': ip_to_str(frame[39:43])}
        if data['dst'] == 'ff:ff:ff:ff:ff:ff':  # An ARP request
            display = data['src'] + ' -> ' + data['dst'] + ' ARP who has ' + data['dst_ip'] + '? Tell ' + \
                      data['src_ip']
        else:
            display = data['src'] + ' -> ' + data['dst'] + ' ARP reply ' + data['src_ip'] + ' -> ' + data['dst_ip']
        return data, display
    elif frame[14] == 0x00:  # IPv4
        # Begin at offset 15
        version, ihl = frame[15] >> 4, frame[15] & 0xf
        if version != 4:
            return None
        data = {'src_ip': ip_to_str(frame[27:31]), 'dst_ip': ip_to_str(frame[31:35])}
        if frame[24] == 17:  # UDP
            offset = 15 + ihl * 4
            data.update({'src_port': (frame[offset] << 8) + frame[offset+1],
                         'dst_port': (frame[offset+2] << 8) + frame[offset+3]})
            display = data['src_ip'] + ':' + str(data['src_port']) + ' -> ' + data['dst_ip'] + ':' + \
                      str(data['dst_port']) + ' UDP'
        else:
            display = data['src_ip'] + ' -> ' + data['dst_ip'] + ' ' + str(frame[24])
        return data, display


def ip_to_str(ip):
    return '.'.join(str(octet) for octet in ip)


def str_to_ip(s):
    return bytes([int(i) for i in s.split('.', 3)])


def replace_arp(frame, src_replace=None, dst_replace=None):
    changed = False
    src_ip = ip_to_str(frame[14+14:14+18])
    if src_replace and src_ip in src_replace:
        frame[14+14:14+18] = str_to_ip(src_replace[src_ip])
        changed = True
    dst_ip = ip_to_str(frame[14+24:14+28])
    if dst_replace and dst_ip in dst_replace:
        frame[14+24:14+28] = str_to_ip(dst_replace[dst_ip])
        changed = True
    return changed


def replace_ip(frame, src_replace=None, dst_replace=None):  # TODO: Efficiency
    changed = False
    src_ip = ip_to_str(frame[14+12:14+16])
    if src_replace and src_ip in src_replace:
        frame[14+12:14+16] = str_to_ip(src_replace[src_ip])
        changed = True
    dst_ip = ip_to_str(frame[14+16:14+20])
    if dst_replace and dst_ip in dst_replace:
        frame[14+16:14+20] = str_to_ip(dst_replace[dst_ip])
        changed = True
    return changed


class VpnNode:
    def __init__(self, ip, i=0, node_map=None, src_replace=None, dst_replace=None, tap=None, sock=None):
        self.ip, self.i = ip, i
        self.node_map = node_map
        self.src_replace, self.dst_replace = src_replace, dst_replace
        self.tap, self.sock = tap, sock
        self.running = False

    # Open a tap device
    def open(self):
        # Open the file descriptor
        f = os.open('/dev/net/tun', os.O_RDWR)
        # Get the interface name
        ifs = ioctl(f, TUNSETIFF, struct.pack(b"16sH", b"fond%d" % self.i, IFF_TAP | IFF_NO_PI))
        if ifs.index(0) == -1:
            sys.exit('Could not get interface name')
        interface = ifs[:ifs.index(0)]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bin_ip = socket.inet_aton(self.ip)
        ifreq = struct.pack(b'16sH2s4s8s', interface, socket.AF_INET, b'\x00' * 2, bin_ip, b'\x00' * 8)
        ioctl(sock, SIOCSIFADDR, ifreq)
        interface = interface.decode('utf-8')
        print('Created interface:', interface, 'on', self.ip, end=' ')
        subprocess.check_call('ifconfig noth%d up' % self.i, shell=True)
        print('...up!')
        self.tap = f

    def bind(self, local_port):
        # Bind to a local socket
        local_ip = '0.0.0.0'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((local_ip, local_port))

    def start(self, local_port, standalone=False):
        if self.tap is None:
            self.open()
        if self.sock is None:
            self.bind(local_port)
        self.sock.settimeout(0.2)
        write = Thread(target=self.write_loop, daemon=True)
        read = Thread(target=self.read_loop, daemon=True)
        self.running = True
        write.start()
        read.start()
        if standalone:
            input()
            self.stop()

    def stop(self):
        self.running = False

    def write_loop(self):
        while self.running:
            # Read in the frame from the tap
            frame = bytearray(os.read(self.tap, 1518))
            if frame:
                frame[:] = bytes([Packet.DATA]) + frame
            try:
                parsed = parse(frame)
            except Exception:
                continue
            if parsed is None:  # Unknown frame
                continue
            data, display = parsed
            print('S', display, end='')
            # Determine whether to send this frame
            if data:
                dst_ip = data['dst_ip']
                if self.node_map and dst_ip in self.node_map:
                    remote_address = self.node_map[dst_ip]
                    self.sock.sendto(frame, remote_address)
                    print(' !')
                else:
                    print()
            else:
                print()

    def read_loop(self):
        while self.running:
            # Read in the frame from the network socket
            try:
                frame, addr = self.sock.recvfrom(1600)
            except socket.timeout:
                continue
            else:
                frame = bytearray(frame)
            try:
                parsed = parse(frame)
            except Exception:
                continue
            if parsed is None:  # Unknown frame
                continue
            data, display = parsed
            print('R', display, end='')
            # Determine whether to receive this frame
            if data:
                dst_ip = data['dst_ip']
                if dst_ip == self.ip:
                    # Strip off the initial Data byte designation
                    os.write(self.tap, frame[1:]), len(frame)
                    print(' !')
                else:
                    print()
            else:
                print()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # ip = '11.0.0.1'
        # i = 1
        # node_map = {'10.0.0.1': ('18.189.101.152', 54174)}
        # src_replace = {'11.0.0.1': '10.0.0.2'}
        # dst_replace = {'11.0.0.2': '10.0.0.1'}
        # port = 54175
        ip = '10.0.0.2'
        i = 1
        node_map = {'10.0.0.1': ('18.24.1.88', 43434)}
        src_replace = dst_replace = None
        port = 43434
    else:
        # ip = '10.0.0.1'
        # i = 0
        # node_map = {'11.0.0.1': ('18.189.101.152', 54175)}
        # src_replace = {'10.0.0.1': '11.0.0.2'}
        # dst_replace = {'10.0.0.2': '11.0.0.1'}
        # port = 54174
        ip = '10.0.0.1'
        i = 0
        node_map = {'10.0.0.2': ('18.96.0.117', 43434)}
        src_replace = dst_replace = None
        port = 43434
    vpn = VpnNode(ip, i, node_map, src_replace, dst_replace)
    vpn.start(port, standalone=True)
