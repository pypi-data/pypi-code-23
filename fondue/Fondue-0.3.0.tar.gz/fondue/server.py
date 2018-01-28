#!/usr/bin/env python3
import socket
from argparse import ArgumentParser

from fondue.packets import HEADER, Packet, parse_packet, PacketError

DEBUG = True
debug = print if DEBUG else lambda *args, **kwargs: None


def start_server(ip='0.0.0.0'):
    print('Starting Fondue server...')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip, 43433))
    debug('Bound to', ip + ':' + '43433')
    while True:
        try:
            b, (ip, port) = s.recvfrom(4096)
        except socket.timeout:
            continue
        # Determine the packet is valid
        try:
            packet = parse_packet(b)
        except PacketError:
            debug('Ignoring invalid packet from', ip + ':' + str(port))
        else:
            if packet['type'] == Packet.GETEXTIP:  # Return the external IP and port to the requester
                debug('[' + ip + ':' + str(port) + '] Get external IP request')
                s.sendto(HEADER + bytes([Packet.SENDEXTIP] + list(socket.inet_aton(ip)) +
                                        [(port >> 8) & 0xff, port & 0xff]), (ip, port))

def main():
    parser = ArgumentParser(prog='fondue-server')
    parser.add_argument('-ip', dest='server_ip', type=str, default='0.0.0.0')
    args = parser.parse_args()
    start_server(args.server_ip)

if __name__ == '__main__':
    main()


