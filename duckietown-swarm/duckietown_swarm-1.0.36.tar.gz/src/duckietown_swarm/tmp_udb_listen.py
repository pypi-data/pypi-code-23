import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 9999))

while(1):
    addr, msg = s.recvfrom(4096)
    print('Received %s from %s' % (addr, msg))
