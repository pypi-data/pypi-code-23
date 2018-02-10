###############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""KibanaClient tests
$Id: test_client.py 4347 2015-08-25 23:57:09Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import json
import unittest

import p01.kibana.client


class FakeSocket(object):
    """Fake socket for receive sending data"""

    def __init__(self):
        self.results = []

    def sendto(self, data, interface):
        """Load data string as json and add to results"""
        data = json.loads(data)
        self.results.append(data)


class FakeClient(p01.kibana.client.KibanaClient):
    """Cleint wrapper with fake _send method"""

    def __init__(self, hostport=None):
        super(FakeClient, self).__init__(hostport)
        self._sock = FakeSocket()
        self.results = self._sock.results

    def results(self):
        return self._sock.results

    # def send(self, data=None, **kwargs):
    #     if data is not None:
    #         kwargs.update(data)
    #     self.results.append(kwargs)


class KibanaClientTest(unittest.TestCase):

    def setUp(self):
        self.client = FakeClient()

    def test_send(self):
        data = {
            u'_index': u'missing',
            u'_source': {
                u'@timestamp': u'...',
                u'@version': 1,
                u'bar': u'bar',
                u'foo': u'foo',
                },
            u'_type': u'missing',
            }
        self.client.send(foo='foo', bar=u'bar')
        result = self.client.results[-1]
        result['_source']['@timestamp'] = u'...'
        self.assertEquals(result, data)

    def test_send_dict(self):
        data = {
            u'_index': u'missing',
            u'_source': {
                u'@timestamp': u'...',
                u'@version': 1,
                u'message': {u'foo': u'bar'},
                },
            u'_type': u'missing',
            }
        self.client.send({'foo': 'bar'})
        result = self.client.results[-1]
        result['_source']['@timestamp'] = u'...'
        self.assertEquals(result, data)

    def test_send_kwargs(self):
        data = {
            u'_index': u'missing',
            u'_source': {
                u'@timestamp': u'...',
                u'@version': 1,
                u'foo': u'bar',
                },
            u'_type': u'missing',
            }
        self.client.send(**{'foo': 'bar'})
        result = self.client.results[-1]
        result['_source']['@timestamp'] = u'...'
        self.assertEquals(result, data)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(KibanaClientTest),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
