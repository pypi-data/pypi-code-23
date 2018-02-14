"""Sniffy is a thin wrapper around pypcap.

This tool will work for the most simple cases. Use tcpdump if you need
something more advanced.
 """
from pcap import pcap
from string import printable

from dpkt.ethernet import Ethernet
from dpkt.ip import IP
from dpkt.tcp import TCP


def addr(bs):
    return '.'.join(str(b) for b in bs)


def packets():
    """Yields tuples with data extracted from captured packages."""
    sniffy = pcap(name=None, promisc=True, immediate=True, timeout_ms=50)

    for timestamp, buf in sniffy:
        eth = Ethernet(buf)
        if not isinstance(eth.data, IP):
            continue
        ip = eth.data
        if not isinstance(ip.data, TCP):
            continue
        tcp = ip.data

        yield addr(ip.src), addr(ip.dst), tcp.data


def main():
    global src, dst, text
    normal_chars = printable[:95]
    for src, dst, data in packets():
        text = data.decode('ascii', 'ignore')
        text = ''.join(c for c in text if c in normal_chars)
        print(f'{src:15} {dst:15} {text}', flush=True)


if __name__ == '__main__':
    main()
