import random
import socket
import time

import netifaces

ifaces = netifaces.interfaces()

B = []

for iface in ifaces:
    print('--- %s --- ' % iface)
    addrs = netifaces.ifaddresses(iface)
    if netifaces.AF_INET in addrs:
        ip4 = addrs[netifaces.AF_INET]
        print ip4
        for _ in ip4:
            if 'broadcast' in _:
                B.append((str(_['addr']), str(_['broadcast'])))

    if netifaces.AF_LINK in addrs:
        MAC = addrs[netifaces.AF_LINK]
        print MAC

print netifaces.gateways()

print('Broadcast addresses: %s' % B)

add2sock = {}
PORT = 9999
for addr, broadcast in B:
    print('connecting %s %s' % (addr, broadcast))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    port = 1240
    while True:
        try:
            print('trying %s %s' % (addr, port))
            sock.bind((addr, port))  # is add correct?
        except Exception as e:
            print e
            port += 1
            continue

        print('ok for %s' % port)
        break

    add2sock[broadcast] = sock

name = socket.gethostname()

while True:
    for broadcast, sock in add2sock.items():
        sock.sendto('Hello from %s' % name, (broadcast, PORT))

    time.sleep(5 + random.uniform(0, 2))
