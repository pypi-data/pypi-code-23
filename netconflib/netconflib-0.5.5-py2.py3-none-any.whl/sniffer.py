"""Sniffer class.

This class gives the ability to show network activity.
"""

import os, time
import threading, queue
from scapy.all import sniff
import logging

class SnifferThread(threading.Thread):
    """This class provides features to display network activity.
    """

    def __init__(self, result_q):
        super(SnifferThread, self).__init__()
        self.logger = logging.getLogger('app.sniffer')
        self.logger.info("Sniffing on network interface...")
        self.result_q = result_q
        self.stoprequest = threading.Event()
        self.counter = 0

    def run(self):
        self.sniff_ethernet()
        while not self.stoprequest.isSet():
            time.sleep(0.1)

    def stop(self):
        self.stoprequest.set()

    def sniff_ethernet(self):
        """Sniff only ping (icmp) packets.
        """

        sniff(filter="icmp", prn=self.custom_action)

    def custom_action(self, packet):
        """Redefining the packet output.

        Arguments:
            packet {object} -- IP packet.
        """

        self.counter += 1
        self.result_q.put(self.getName(), self.counter)
        return 'Packet #{}: {} ==> {}'.format(self.counter, packet[0][1].src, packet[0][1].dst)