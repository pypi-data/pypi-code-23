from duckietown_swarm.dcache import CouldNotReadEnvelope
import socket
import time

from multiaddr import Multiaddr
import netifaces

from .dcache import Envelope
from .dcache_wire import create_propose_message

UDP_PORT = 1240


def get_suitable_udp_interfaces():
    ifaces = netifaces.interfaces()

    B = {}

    for iface in ifaces:

        # exclude docker interfaces
        if 'docker' in iface:
            continue
#        print('--- %s --- ' % iface)
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            ip4 = addrs[netifaces.AF_INET]
            for _ in ip4:
                if 'broadcast' in _:
                    B[iface] = {'address': str(_['addr']),
                              'broadcast': str(_['broadcast'])}

#        if netifaces.AF_LINK in addrs:
#            MAC = addrs[netifaces.AF_LINK]
#            print MAC

#    print('Broadcast addresses: %s' % B)
    return B


def udp_broadcaster(mi):
    addr = mi.my_maddr
    m1 = Multiaddr(addr)

    # get the multiaddr protocol description objects
    p = m1.protocols()

    # [Protocol(code=4, name='ip4', size=32), Protocol(code=17, name='udp', size=16)]
    assert p[0].name == 'ip4'
    assert p[1].name == 'udp'
    # /ip4/IP/udp/port

    broadcast_address = m1.value_for_protocol(p[0].code)
    broadcast_port = int(m1.value_for_protocol(p[1].code))

    my_address = None
    for name, x in get_suitable_udp_interfaces().items():
        if x['broadcast'] == broadcast_address:
            my_address = x['address']
#            my_name = name
            print('Using interface %s = %s' % (name, x))

    if my_address is None:
        msg = 'Could not find address for broadcast address %s.' % my_address
        raise Exception(msg)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    port = UDP_PORT
    while True:
        try:
            sock.bind((my_address, port))  # is add correct?
        except Exception as e:
            print('could not bind to %s:%s' % (my_address, port))
            print e
            port += 1
            if port > 2000:
                raise
            continue

        if port != UDP_PORT:
            print('finally bound to %s:%s' % (my_address, port))

#        print('ok for %s' % port)
        break

    while True:
        envelope = mi.get_next_for_me()
#        envelope.maddr_to += '/dswarm/*/brain'
        envelope_json = envelope.to_json()
        sock.sendto(envelope_json, (broadcast_address, broadcast_port))


def udp_listener(mi):

    m1 = Multiaddr(mi.my_maddr)

    # get the multiaddr protocol description objects
    p = m1.protocols()

    # [Protocol(code=4, name='ip4', size=32), Protocol(code=17, name='udp', size=16)]
    assert p[0].name == 'ip4'
    assert p[1].name == 'udp'
    # /ip4/IP/udp/port

    broadcast_address = m1.value_for_protocol(p[0].code)
    broadcast_port = int(m1.value_for_protocol(p[1].code))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((broadcast_address, broadcast_port))
    except Exception as e:
        msg = 'Could not bind UDP listener to %s:%s' % (broadcast_address, broadcast_port)
        msg += ' ' + str(e)
        raise Exception(msg)

    t = time.time()
    msg = create_propose_message(('pri', mi.key.hash, 'addresses'),
                                 mi.my_maddr, validity=[t, t + 300])
    mi.send_to_brain('', msg, sign=True)

    while True:
        msg, (who_host, who_port) = sock.recvfrom(4096)
        try:
            env = Envelope.from_json(msg)
        except CouldNotReadEnvelope as e:
            print(e)
            continue
#        e.maddr_from = '/ip4/%s/udp/%s' % (who_host, who_port) + e.maddr_from

#        print('received \n from: %s\n   to: %s' % (e.maddr_from, e.maddr_to))
        mi.dispatch(env)
#        mi.send_to_brain('', e.contents)
