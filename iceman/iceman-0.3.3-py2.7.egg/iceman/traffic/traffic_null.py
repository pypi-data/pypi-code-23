# -*- coding: utf-8 -*-
"""iceman/traffic/traffic_null.py
"""
from multiprocessing import Queue, Lock

import nfqueue


class TrafficNull(object):
    """Empty IP Packet Traffic Judge for testing

    :param egress_queue: nfqueue number
    :type egress_queue: int

    :param ingress_queue: nfqueue number
    :type ingress_queue: int

    :param cipher_suite: unused
    :type cipher_suite: instance

    :param encryption_enabled: unused
    :type encryption_enabled: bool
    """

    def __init__(self, egress_queue, ingress_queue, cipher_suite, encryption_enabled):
        self.egress_queue = egress_queue
        self.ingress_queue = ingress_queue
        self.cipher_suite = cipher_suite
        self.encryption_enabled = encryption_enabled

        #error output log queue
        self.error_log = Queue()
        self.error_lock = Lock()

    def handle_egress(self, not_used, payload): # pylint: disable=unused-argument
                                                # pylint: disable-msg=R0915
        """egress traffic handler
        """
        payload.set_verdict(nfqueue.NF_ACCEPT)
        return 0


    def handle_ingress(self, not_used, payload): # pylint: disable=unused-argument
                                                 # pylint: disable-msg=R0915
        """nfqueue callback
        """
        payload.set_verdict(nfqueue.NF_ACCEPT)
        return 0
