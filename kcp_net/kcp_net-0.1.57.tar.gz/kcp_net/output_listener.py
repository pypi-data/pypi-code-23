# coding: utf8

import kcp_wrapper


class OutputListener(kcp_wrapper.OutputListener):
    sock = None
    address = None

    def __init__(self, sock, address):
        kcp_wrapper.OutputListener.__init__(self)
        self.sock = sock
        self.address = address

    def call(self, data, kcp_obj):
        # print 'output:', repr(data)
        self.sock.sendto(data, self.address)
        return 0
