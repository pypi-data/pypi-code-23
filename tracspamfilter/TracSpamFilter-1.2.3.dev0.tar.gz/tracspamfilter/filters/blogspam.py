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

import json
from email.utils import parseaddr

from trac.config import IntOption, Option, ListOption
from trac.core import Component, implements
from trac.mimeview.api import is_binary
from tracspamfilter.api import IFilterStrategy, N_, user_agent
from tracspamfilter.timeoutserverproxy import TimeoutHTTPConnection
from tracspamfilter.filters.trapfield import TrapFieldFilterStrategy


class BlogSpamFilterStrategy(Component):
    """Spam filter using the BlogSpam service (http://blogspam.net/).
    """
    implements(IFilterStrategy)

    karma_points = IntOption('spam-filter', 'blogspam_karma', '5',
        """By how many points an BlogSpam reject impacts the overall
        karma of a submission.""", doc_domain='tracspamfilter')

    api_url = Option('spam-filter', 'blogspam_json_api_url',
        'test.blogspam.net:9999', "URL of the BlogSpam service.",
        doc_domain='tracspamfilter')

    skip_tests = ListOption('spam-filter', 'blogspam_json_skip_tests',
        '45-wordcount.js, 60-drone.js, 80-sfs.js',
        doc="Comma separated list of tests to skip.",
        doc_domain='tracspamfilter')

    # IFilterStrategy implementation

    def is_external(self):
        return True

    def test(self, req, author, content, ip):
        if not self._check_preconditions(req, author, content):
            return

        try:
            resp = self._post(req, author, content, ip)
            if resp[0] != 200:
                raise Exception("Return code %s" % resp[0])
            resp = resp[1]
            if resp['result'] == 'SPAM':
                return (-abs(self.karma_points),
                        N_("BlogSpam says content is spam (%s [%s])"),
                        resp['reason'], resp['blocker'])
        except Exception, v:
            self.log.warning("Checking with BlogSpam failed: %s", v)

    def train(self, req, author, content, ip, spam=True):
        if not self._check_preconditions(req, author, content):
            return -2

        try:
            if spam:
                resp = self._post(req, author, content, ip, 'spam')
            else:
                resp = self._post(req, author, content, ip, 'ok')
            if resp[0] != 200:
                raise Exception("Return code %s" % resp[0])
            self.log.debug("Classifying with BlogSpam succeeded.")
            return 1
        except Exception, v:
            self.log.warning("Classifying with BlogSpam failed: %s", v)
        except IOError, v:
            self.log.warning("Classifying with BlogSpam failed: %s", v)
        return -1

    def getmethods(self):
        try:
            resp = self._call('GET', '%s/plugins' % self.api_url, None)
            if resp[0] != 200:
                raise Exception("Return code %s" % resp[0])
            return resp[1]
        except Exception, v:
            self.log.warning("Getting BlogSpam methods failed: %s", v)
            return None

    # Internal methods

    def _check_preconditions(self, req, author, content):
        if self.karma_points == 0:
            return False

        if len(content) == 0:
            return False

        if is_binary(content):
            self.log.warning("Content is binary, BlogSpam content check "
                             "skipped")
            return False

        return True

    def _post(self, req, author, content, ip, train=None):
        # Split up author into name and email, if possible
        author = author.encode('utf-8')
        author_name, author_email = parseaddr(author)
        if not author_name and not author_email:
            author_name = author
        elif not author_name and author_email.find("@") < 1:
            author_name = author
            author_email = None

        params = {
            'ip': ip,
            'name': author_name,
            'comment': content.encode('utf-8'),
            'agent': req.get_header('User-Agent'),
            'site': req.base_url,
            'version': user_agent
        }
        if len(self.skip_tests):
            params['options'] = 'exclude=%s' % \
                                ',exclude='.join(self.skip_tests)
        if author_email:
            params['email'] = author_email
        trap_link = TrapFieldFilterStrategy(self.env).getlink(req)
        if trap_link:
            params['link'] = trap_link

        if train is not None:
            params['train'] = train
            return self._call('POST', '%s/classify' % self.api_url, params)
        else:
            return self._call('POST', '%s/' % self.api_url, params)

    def _call(self, method, url, data=None):
        """ Do the actual HTTP request """
        offs = url.find('/')
        api_host = url[:offs]
        path = url[offs:]
        conn = TimeoutHTTPConnection(api_host)
        headers = {'User-Agent': user_agent}

        if data:
            headers.update({'Content-type': 'application/json'})
            conn.request(method, path, json.dumps(data), headers)
        else:
            conn.request(method, path, None, headers)

        response = conn.getresponse()
        body = response.read()
        if body != "OK":
            body = json.loads(body)
        result = [response.status, body]
        conn.close()
        return result
