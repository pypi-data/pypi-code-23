from __future__ import print_function

import sys

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

addr = "224.0.0.234"
port = 9999

name = sys.argv[1]


class MulticastPingPong(DatagramProtocol):

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)
        # Join a specific multicast group:
        self.transport.joinGroup(addr)

    def datagramReceived(self, datagram, address):
        print("Datagram %s received from %s" % (repr(datagram), repr(address)))
        if 'Ping' in datagram:
            # Rather than replying to the group multicast address, we send the
            # reply directly (unicast) to the originating port:
            self.transport.write(b"Server %s: Pong" % name, address)


# We use listenMultiple=True so that we can run MulticastServer.py and
# MulticastClient.py on same machine:
reactor.listenMulticast(port, MulticastPingPong(), interface='0.0.0.0', listenMultiple=True)
reactor.run()
