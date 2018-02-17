from __future__ import print_function

import sys

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

name = sys.argv[1]

#$ netstat -gn
#IPv6/IPv4 Group Memberships
#Interface       RefCnt Group
#--------------- ------ ---------------------
#lo              1      224.0.0.1
#ens33           1      224.0.0.251
#ens33           1      224.0.0.1
#ens38           1      228.0.0.5
#ens38           1      224.0.0.251
#ens38           1      224.0.0.1
#docker0         1      224.0.0.251
#docker0         1      224.0.0.1

#ens33     Link encap:Ethernet  HWaddr 00:0c:29:c4:74:c8
#          inet addr:192.168.134.128  Bcast:192.168.134.255  Mask:255.255.255.0

addr = "224.0.0.234"
port = 9999


class MulticastPingClient(DatagramProtocol):

    def startProtocol(self):
        # Join the multicast address, so we can receive replies:
        self.transport.joinGroup(addr)
        # Send to 228.0.0.5:9999 - all listeners on the multicast address
        # (including us) will receive this message.
        self.transport.write(b'Client %s: Ping' % name, (addr, port))

    def datagramReceived(self, datagram, address):
        print("Datagram %s received from %s" % (repr(datagram), repr(address)))


# interface='192.168.134.128'
reactor.listenMulticast(port, MulticastPingClient(), interface='0.0.0.0', listenMultiple=True)
reactor.run()
