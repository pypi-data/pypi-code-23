import socket
import sys


def main():
    if len(sys.argv) > 1:
        ip = '10.0.0.2'
        other = '10.0.0.1'
    else:
        ip = '10.0.0.1'
        other = '10.0.0.2'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip, 43435))
    print('Bound to', ip + ':43435')
    while True:
        s.sendto(bytes([42, 42, 42, 42]), (other, 43435))
        input('Send again?')

