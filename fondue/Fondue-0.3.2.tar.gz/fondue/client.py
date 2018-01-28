#!/usr/bin/env python3
import socket
import select
import os
import sys
from argparse import ArgumentParser
from time import sleep
from threading import Thread
from timeit import default_timer as timer

from fondue import __version__
from fondue.packets import HEADER, Packet, parse_packet, PacketError
from fondue.vpn import VpnNode

DEBUG = True
debug = print if DEBUG else lambda *args, **kwargs: None

SERVERS = [('18.96.0.117', 43433)]  # TODO: Add more servers


class Client:
    def __init__(self, port=43434):
        self.port = port
        self.connected = False
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('0.0.0.0', port))

    # Repeatedly multicast data, to a list of addresses, until a certain type of packet is received, then returns the
    # packet.
    def multicast(self, data, addrs, wait_for_types, verify=True):
        self.s.settimeout(0.5)
        i = -1
        while True:
            i = (i+1) % len(addrs)  # Cycle through addresses
            self.s.sendto(data, addrs[i])
            # Continue on timeouts
            try:
                b, sender_addr = self.s.recvfrom(4096)
            except socket.timeout:
                continue
            print(sender_addr)
            # Verify the sender as one of the destinations
            if verify and sender_addr not in addrs:
                continue
            try:
                packet = parse_packet(b)
            except PacketError:
                continue
            else:
                if packet['type'] in wait_for_types:
                    return packet

    # Like multicast, but a single address
    def broadcast(self, data, addr, wait_for_types, verify=True):
        return self.multicast(data, [addr], wait_for_types, verify)

    # Attempt to get and return the internal address of the client
    def get_internal_address(self):
        tcp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tcp.connect(('8.8.8.8', 80))  # TODO: Change from Google's DNS
        return tcp.getsockname()[0], self.port

    # Get and return the external address of the client
    def get_external_address(self):
        data = self.multicast(HEADER + bytes([Packet.GETEXTIP]), SERVERS, [Packet.SENDEXTIP])['data']
        if len(data) != 6:  # 4 bytes for the IPv4 address, 2 for the port
            raise PacketError('Invalid SENDEXTIP response')
        # External address received
        ext_addr = socket.inet_ntoa(data[:4]), data[4] << 8 | data[5]
        return ext_addr

    def find_timeout(self, peer, max_time=10):
        t = 1
        while t <= max_time:
            self.s.settimeout(t)
            self.s.sendto(HEADER + bytes([Packet.TIMING]), peer)
            sleep(t)
            try:
                recv, addr = self.s.recvfrom(4096)
            except socket.timeout:
                return t-1
            else:
                if addr == peer:
                    t += 1
        return t

    def keepalive(self, peer, interval):
        self.connected = True
        self.s.settimeout(0)
        while self.connected:
            try:
                self.s.sendto(HEADER + bytes([Packet.KEEPALIVE]), peer)
            except Exception as e:
                print(e, 'Aborting connection.')
                self.connected = False
            else:
                sleep(interval)

    def connect_to_peer(self, peer_addr):
        peer_ip, peer_port = peer_addr
        self.s.setblocking(False)  # Set timeout
        broadcast = Packet.PEER1
        start = timer()
        while True:
            readable, writable, error = select.select([self.s], [self.s], [self.s])
            for err in error:
                if err == self.s:
                    print('An error occurred.')
                    quit()  # TODO
            for write in writable:
                if write == self.s:
                    now = timer()
                    if now - start > 1.0:
                        self.s.sendto(HEADER + bytes([broadcast]), (peer_ip, peer_port))
                        start = now
            for read in readable:
                if read == self.s:
                    recv, (sender_addr, sender_port) = self.s.recvfrom(4096)
                    print(sender_addr)
                    try:
                        packet = parse_packet(recv)
                    except PacketError:
                        continue
                    if peer_ip != sender_addr:  # Ignore unsolicited packets
                        continue
                    if peer_port != sender_port:  # Switch ports
                        print('Switching peer port to:', sender_port)
                        peer_port = sender_port
                    # If we receive any peering packets and are broadcasting the first, broadcast the second
                    if packet['type'] in [Packet.PEER1, Packet.PEER2, Packet.PEER3] and broadcast == Packet.PEER1:
                        print('Received one peering packet, confirming bidirectionality...')
                        broadcast = Packet.PEER2
                    elif packet['type'] in [Packet.PEER2, Packet.PEER3] and broadcast == Packet.PEER2:
                        print('Bidirectionality confirmed, syncing...')
                        broadcast = Packet.PEER3
                    elif packet['type'] == Packet.PEER3 and broadcast == Packet.PEER3:
                        return (peer_ip, peer_port)

    # Perform NAT punchthrough and connect to a peer
    def punchthrough(self):
        int_addr = self.get_internal_address()
        print('Internal address:', int_addr[0] + ':' + str(int_addr[1]))
        ext_addr = self.get_external_address()
        if int_addr != ext_addr:
            print('You are behind a NAT service. Punchthrough is required.')
        print('Peer enters this address:', ext_addr[0] + ':' + str(ext_addr[1]))
        peer_addr = input('Enter peer external address: ')
        peer_addr = peer_addr.split(':', 1)
        peer_addr = peer_addr[0], int(peer_addr[1])
        print('Peering...')
        peer_addr = self.connect_to_peer(peer_addr)
        Thread(target=self.keepalive, args=(peer_addr, 5), daemon=True).start()
        print('Starting VPN node...')
        selfnum = ext_addr[0] + str(ext_addr[1])
        peernum = peer_addr[0] + str(peer_addr[1])
        # Determine who gets which IP address
        if selfnum > peernum:
            ip = '10.0.0.1'
            node_map = {'10.0.0.2': peer_addr}
        else:
            ip = '10.0.0.2'
            node_map = {'10.0.0.1': peer_addr}
        node = VpnNode(ip, i=0, node_map=node_map, sock=self.s)
        node.start(0, standalone=True)


def main():
    # Only works for UNIX
    if os.geteuid() != 0:
        # sudo or fondue here?
        args = ['sudo', sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *args)
    parser = ArgumentParser(prog='fondue')
    parser.add_argument('-p', dest='port', default=43434, type=int)
    args = parser.parse_args()
    c = Client(args.port)
    print('== Fondue', __version__, '==')
    c.punchthrough()


if __name__ == '__main__':
    main()
