from duckietown_swarm.dcache import BOOTSTRAP_PATTERNS
from duckietown_swarm.dcache_wire import create_request_message
from duckietown_swarm.utils import now_until
import socket
import time

import netifaces

from .dcache import CouldNotReadEnvelope
from .dcache import Envelope
from .dcache_wire import create_propose_message

UDP_PORT = 1240


def get_suitable_udp_interfaces():
    ifaces = netifaces.interfaces()

    B = {}

    for iface in ifaces:
        iface = str(iface)
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


def get_mac_addresses():
    '''
        returns map ifname -> MAC
    '''
    ifaces = netifaces.interfaces()

    B = {}
    for iface in ifaces:
        addrs = netifaces.ifaddresses(iface)
        iface = str(iface)
        if netifaces.AF_LINK in addrs:
            addresses = addrs[netifaces.AF_LINK]
# https://pypi.python.org/pypi/netifaces
# You might be wondering why this value is a list. The reason is that it's
#  possible for an interface to have more than one address, even within the same family.
#  I'll say that again:
# you can have more than one address of the same type associated with each interface.
#
# Asking for "the" address of a particular interface doesn't make sense.

            for i, _ in enumerate(addresses):
                MAC = _['addr']

                if len(addresses) == 1:
                    name = iface
                else:
                    name = iface + ['a', 'b', 'c', 'd'][i % 4]
                B[name] = str(MAC)
    return B


def udp_broadcaster(mi, interface, broadcast_port):
    addr = mi.my_maddr

    interfaces = get_suitable_udp_interfaces()
    if not interface in interfaces:
        msg = 'No interface %s available' % interface
        raise Exception(msg)

    broadcast_address = interfaces[interface]['broadcast']
    my_address = interfaces[interface]['address']
    ipfsi = mi.get_ipfsi()
    identity = ipfsi.ipfs_id()
    bucket = ('pri', identity, 'udp')
    t = time.time()
    msg = create_propose_message(bucket, addr, validity=[t, t + 60 * 10])
    mi.send_to_brain('', msg, sign=True)

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

    msg = create_request_message(BOOTSTRAP_PATTERNS, validity=now_until(105))
    maddr_from = '/dswarm/%s/brain' % ipfsi.ipfs_id()
    # otherwise I will answer to myself
#    maddr_from = '/dswarm/*/brain'  #% ipfsi.ipfs_id()
    envelope = Envelope(maddr_from=maddr_from,
                 maddr_to='/dswarm/*/brain',
                 contents=msg)
    q = mi.name2queue[mi.my_maddr]
    q.put(envelope)

    while True:
        envelope = mi.get_next_for_me()
        envelope_json = envelope.to_json()
        sock.sendto(envelope_json, (broadcast_address, broadcast_port))


def udp_listener(mi, interface, broadcast_port):

#    m1 = Multiaddr(mi.my_maddr)
#
#    # get the multiaddr protocol description objects
#    p = m1.protocols()

#    # [Protocol(code=4, name='ip4', size=32), Protocol(code=17, name='udp', size=16)]
#    assert p[0].name == 'ip4'
#    assert p[1].name == 'udp'
    # /ip4/IP/udp/port
#
#    broadcast_address = m1.value_for_protocol(p[0].code)
#    broadcast_port = int(m1.value_for_protocol(p[1].code))

    interfaces = get_suitable_udp_interfaces()

    if not interface in interfaces:
        msg = 'No interface %s available' % interface
        raise Exception(msg)

    broadcast_address = interfaces[interface]['broadcast']
#    my_address = interfaces[interface]['my_address']

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

    from duckietown_swarm.irc2 import CouldNotDispatch

    while True:
        msg, (_who_host, _who_port) = sock.recvfrom(4096)
        try:
            env = Envelope.from_json(msg)
        except CouldNotReadEnvelope as e:
            print(e)
            continue
        else:
            try:
                mi.dispatch(env)
            except CouldNotDispatch as e:
                pass  # print('Ignoring dispatch error for %s' % env.maddr_to)
