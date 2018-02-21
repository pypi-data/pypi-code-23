# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Edgewall Software
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
# Author: Dirk Stöcker <trac@dstoecker.de>

import re
from dns.name import from_text
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers, Timeout, query

from trac.config import IntOption, ListOption
from trac.core import Component, implements

from tracspamfilter.api import IFilterStrategy, N_


class URLBlacklistFilterStrategy(Component):
    """Spam filter based on URL blacklistings.

    Requires the dnspython module from http://www.dnspython.org/.
    """
    implements(IFilterStrategy)

    karma_points = IntOption('spam-filter', 'url_blacklist_karma', '3',
        """By how many points blacklisting by a single bad URL impacts the
        overall karma of a submission.""", doc_domain='tracspamfilter')

    servers_default = 'urired.spameatingmonkey.net,multi.surbl.org,' \
                      'dbl.spamhaus.org'
    servers = ListOption('spam-filter', 'url_blacklist_servers',
        servers_default, doc="Servers used for URL blacklisting.",
        doc_domain='tracspamfilter')

    # IFilterStrategy implementation

    def is_external(self):
        return True

    def test(self, req, author, content, ip):
        if not self._check_preconditions(req, author, content, ip):
            return

        urls = self._geturls(author + "\n" + content)

        if not urls:
            return

        self.log.debug('Checking for URL blacklisting on "%s"',
                       ", ".join(urls))

        points = 0
        servers = []

        for server in self.servers:
            for url in sorted(urls.keys()):
                self.log.debug("Checking blacklist %s for %s", server, url)
                try:
                    servers.append(self._query(url, server))
                    points -= abs(self.karma_points)
                except NXDOMAIN:  # not blacklisted on this server
                    #if url.startswith("www.") and not url[4:] in urls:
                    #    try:
                    #        self.log.debug("Checking blacklist %s for %s",
                    #                       server, url[4:])
                    #        servers.append("[www.]%s" % self._query(url[4:], server))
                    #        points -= abs(self.karma_points)
                    #    except:
                    #        pass
                    continue
                except (Timeout, NoAnswer, NoNameservers), e:
                    self.log.warning('Error checking URL blacklist server '
                                     '"%s" for URL "%s": %s', server, url, e)

        if points != 0:
            return points, N_("URL's blacklisted by %s"), ', '.join(servers)

    def train(self, req, author, content, ip, spam=True):
        return 0

    # Internal methods

    def _query(self, url, server):
        res = query(from_text(url + '.' + server.encode('utf-8')))[0].to_text()
        if res == '127.0.0.1':
            return '%s (%s)' % (server, url)
        # strip the common part of responses
        if res.startswith('127.0.0.'):
            res = res[8:]
        elif res.startswith('127.'):
            res = res[4:]
        return '%s (%s[%s])' % (server, url, res)

    def _check_preconditions(self, req, author, content, ip):
        if self.karma_points == 0 or not self.servers:
            return False

        return True

    def _geturls(self, content):
        urls = {}
        content = content.lower()
        # no IDN domains, only punnycode
        urlstr = re.compile("^([a-z0-9][a-z0-9.-]+[a-z0-9])(.?)")

        while 1:
            pos = content.find('//')
            if pos < 0:
                break
            content = content[pos + 2:]
            res = urlstr.search(content)
            if res:
                u = res.group(1)
                urls[u] = urls.get(u, 0)
                if res.group(2) not in ('"', '\'', '/', '\n', '.', '!',
                                        '?', ',', ';', ''):
                    self.log.warn("Strange URL '%s' found.", u)
        return urls
