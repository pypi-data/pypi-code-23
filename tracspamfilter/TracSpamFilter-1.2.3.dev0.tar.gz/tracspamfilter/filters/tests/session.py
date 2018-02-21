# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.


import unittest

from trac.test import EnvironmentStub, MockRequest

from tracspamfilter.filters.session import SessionFilterStrategy


class SessionFilterStrategyTestCase(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentStub(enable=[SessionFilterStrategy])
        self.strategy = SessionFilterStrategy(self.env)

    def test_new_session(self):
        req = MockRequest(self.env)
        req.session.last_visit = 42
        rv = self.strategy.test(req, None, None, '127.0.0.1')
        self.assertEqual((2, "Existing session found"), rv)

    def test_session_name_set(self):
        req = MockRequest(self.env)
        req.session.last_visit = 42
        req.session['name'] = 'joe'
        rv = self.strategy.test(req, None, None, '127.0.0.1')
        self.assertEqual((4, "Existing session found"), rv)

    def test_session_email_set(self):
        req = MockRequest(self.env)
        req.session.last_visit = 42
        req.session['email'] = 'joe@example.com'
        rv = self.strategy.test(req, None, None, '127.0.0.1')
        self.assertEqual((4, "Existing session found"), rv)

    def test_session_email_set_but_invalid(self):
        req = MockRequest(self.env)
        req.session.last_visit = 42
        req.session['email'] = 'joey'
        rv = self.strategy.test(req, None, None, '127.0.0.1')
        self.assertEqual((2, "Existing session found"), rv)

    def test_session_name_and_email_set(self):
        req = MockRequest(self.env)
        req.session.last_visit = 42
        req.session['name'] = 'joe'
        req.session['email'] = 'joe@example.com'
        rv = self.strategy.test(req, None, None, '127.0.0.1')
        self.assertEqual((6, "Existing session found"), rv)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SessionFilterStrategyTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
