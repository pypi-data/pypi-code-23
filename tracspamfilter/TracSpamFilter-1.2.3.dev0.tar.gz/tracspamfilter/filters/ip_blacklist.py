# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Edgewall Software
# Copyright (C) 2006 Matthew Good <trac@matt-good.net>
# Copyright (C) 2015 Dirk Stöcker <trac@dstoecker.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.
#
# Author: Matthew Good <trac@matt-good.net>

from dns.ipv6 import inet_aton as ipv6_inet_aton
from dns.name import from_text
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers, Timeout, query

from trac.config import ListOption, IntOption
from trac.core import Component, implements

from tracspamfilter.api import IFilterStrategy, N_


class IPBlacklistFilterStrategy(Component):
    """Spam filter based on IP blacklistings.

    Requires the dnspython module from http://www.dnspython.org/.
    """
    implements(IFilterStrategy)

    karma_points = IntOption('spam-filter', 'ip_blacklist_karma', '5',
        """By how many points blacklisting by a single server impacts the
        overall karma of a submission.""", doc_domain='tracspamfilter')

    servers_default = 'all.s5h.net,dnsbl.dronebl.org,rbl.blockedservers.com'
    servers = ListOption('spam-filter', 'ip_blacklist_servers',
        servers_default, doc="Servers used for IPv4 blacklisting.",
        doc_domain='tracspamfilter')

    servers6_default = 'all.s5h.net,dnsbl.dronebl.org,' \
                       'bl.ipv6.spameatingmonkey.net'
    servers6 = ListOption('spam-filter', 'ip6_blacklist_servers',
        servers6_default, doc="Servers used for IPv6 blacklisting.",
        doc_domain='tracspamfilter')

    # IFilterStrategy implementation

    def is_external(self):
        return True

    def test(self, req, author, content, ip):
        if self.karma_points == 0:
            return

        serverlist, prefix = self._getdata(ip)
        if not serverlist:
            self.log.warning("No IP blacklist servers configured")
            return

        self.log.debug('Checking for IP blacklisting on "%s"', ip)

        points = 0
        servers = []

        for server in serverlist:
            self.log.debug("Checking blacklist %s for %s [%s]", server, ip,
                           prefix)
            try:
                res = query(from_text(prefix +
                                      server.encode('utf-8')))[0].to_text()
                points -= abs(self.karma_points)
                if res == '127.0.0.1':
                    servers.append(server)
                else:
                    # strip the common part of responses
                    if res.startswith('127.0.0.'):
                        res = res[8:]
                    elif res.startswith('127.'):
                        res = res[4:]
                    servers.append('%s [%s]' % (server, res))
            except NXDOMAIN:  # not blacklisted on this server
                continue
            except (Timeout, NoAnswer, NoNameservers), e:
                self.log.warning('Error checking IP blacklist server "%s" '
                                 'for IP "%s": %s', server, ip, e)

        if points != 0:
            return (points, N_("IP %s blacklisted by %s"), ip,
                    ', '.join(servers))

    def train(self, req, author, content, ip, spam=True):
        return 0

    # Internal methods

    def _getdata(self, ip):
        if ip.find(".") < 0:
            encoded = reversed(list(ipv6_inet_aton(ip).encode('hex_codec')))
            return self.servers6, '.'.join(encoded) + '.'
        return self.servers, '.'.join(reversed(ip.split('.'))) + '.'
