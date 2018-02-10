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
"""KibanaServer tests
$Id: test_server.py 4742 2018-02-10 16:46:47Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest

import p01.kibana.server


class KibanaServerTest(unittest.TestCase):

    def setUp(self):
        interface = '0.0.0.0:2200'
        esoptions = {'hosts': ['0.0.0.0:9200']}
        self.svc = p01.kibana.server.KibanaServer(interface, esoptions)

    def test_construct(self):
        esoptions = {'hosts': ['0.0.0.0:9200']}
        svc = p01.kibana.server.KibanaServer('2200', esoptions)
        self.assertEquals(svc._host, '')
        self.assertEquals(svc._port, 2200)
        self.assertEquals(svc._interval, 5.0)
        self.assertEquals(svc._debug, 0)
        self.assertEquals(svc._backend._hosts, ['0.0.0.0:9200'])
        esoptions = {'hosts': ['foo:9200']}
        svc = p01.kibana.server.KibanaServer('bar:2200', esoptions, debug=True)
        self.assertEquals(svc._host, 'bar')
        self.assertEquals(svc._port, 2200)
        self.assertEquals(svc._backend._hosts, ['foo:9200'])
        self.assertEquals(svc._debug, False)
        self.assertEquals(svc._loglevel, 0)

    def test_backend(self):
        esoptions = {'hosts': ['bar:9200']}
        p01.kibana.server.KibanaServer._send = lambda self, x, y: None
        svc = p01.kibana.server.KibanaServer('2200', esoptions)
        self.assertEquals(svc._backend._hosts, ['bar:9200'])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(KibanaServerTest),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


