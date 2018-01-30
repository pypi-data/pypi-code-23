# -*- coding: utf-8 -*-

import re
import errno
import random
import socket

import codecs
import six

from ..deprecated import deprecated

import logging
logger = logging.getLogger(__name__)


@deprecated("use get_free_port instead")
def get_tcpport_not_in_use(a=40000, b=65535):
    logger.info("random a tcpport not in use, range from %d to %d", a, b)
    while True:
        sock = socket.socket()
        port = random.randint(a, b)
        addr = ("0.0.0.0", port)
        try:
            sock.bind(addr)
        except socket.error as err:
            if err.errno == errno.EADDRINUSE:
                logger.debug("addr <%d:%d> is in use, random another port", a, b)
                continue
            else:
                raise
        else:
            return port
        finally:
            sock.close()


def get_free_port():
    sock = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', 0))
        _, port = sock.getsockname()
    finally:
        sock.close()
    return port


def is_ipv4(ip):
    """
    Returns True if the IPv4 address ia valid, otherwise returns False.
    """
    try:
        socket.inet_aton(ip)
    except socket.error:
        return False
    return True


def randmac(is_multicast=False, is_locally_administered=False, oui=None, upper=True):
    if oui is None:
        mac = [random.randint(0, 255) for _ in range(0, 6)]
        mac[0] &= 0xfc
        if is_multicast:
            mac[0] |= 0b01

        if is_locally_administered:
            mac[0] |= 0b10
    else:
        mac = []

        mac.extend([int(h, 16) for h in oui.split(':')])
        mac.extend([random.randint(0, 255) for _ in range(0, 3)])

    fmt = "%02X" if upper else "%02x"
    return ':'.join([fmt % i for i in mac])


def trim_mac(addr, separate=':', upper=True):
    new = []
    addr = addr.strip()
    if re.search(r'[:-]', addr):
        segments = re.split(r'[:-]', addr)
        for segment in segments:
            segment = segment.zfill(2)
            new.append(segment)
    else:
        if six.PY2:
            for segment in addr.decode('hex'):
                segment = segment.encode('hex')
                new.append(segment)
        else:
            for i in codecs.decode(addr.encode(), "hex"):
                new.append("%02x" % i)
    new_addr = separate.join(new[0:6])
    if upper:
        return new_addr.upper()
    else:
        return new_addr.lower()
