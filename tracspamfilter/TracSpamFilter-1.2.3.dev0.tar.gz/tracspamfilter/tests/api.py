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

import time
import unittest

from trac.core import Component, implements
from trac.test import EnvironmentStub, MockRequest

from tracspamfilter.api import IFilterStrategy, RejectContent
from tracspamfilter.filtersystem import FilterSystem
from tracspamfilter.model import LogEntry
from tracspamfilter.tests.model import reset_db


class DummyStrategy(Component):
    implements(IFilterStrategy)

    def __init__(self):
        self.test_called = self.train_called = False
        self.req = self.author = self.content = None
        self.karma = 0
        self.message = None
        self.spam = None

    def configure(self, karma, message="Dummy"):
        self.karma = karma
        self.message = message

    def test(self, req, author, content, ip):
        self.test_called = True
        self.req = req
        self.author = author
        self.content = content
        self.ip = ip
        return self.karma, self.message

    def train(self, req, author, content, ip, spam=True):
        self.train_called = True
        self.req = req
        self.author = author
        self.content = content
        self.ip = ip
        self.spam = spam

    def is_external(self):
        return False

class FilterSystemTestCase(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentStub(enable=[FilterSystem, DummyStrategy])
        FilterSystem(self.env).upgrade_environment()

    def tearDown(self):
        reset_db(self.env)

    def test_trust_authenticated(self):
        self.env.config.set('spam-filter', 'trust_authenticated', True)
        req = MockRequest(self.env, authname='john', path_info='/foo')
        FilterSystem(self.env).test(req, '', [])
        self.assertFalse(DummyStrategy(self.env).test_called)

    def test_dont_trust_authenticated(self):
        self.env.config.set('spam-filter', 'trust_authenticated', False)
        req = MockRequest(self.env, authname='john', path_info='/foo')
        FilterSystem(self.env).test(req, '', [])
        self.assertTrue(DummyStrategy(self.env).test_called)

    def test_without_oldcontent(self):
        req = MockRequest(self.env, path_info='/foo')
        FilterSystem(self.env).test(req, 'John Doe', [(None, 'Test')])
        self.assertEqual('Test', DummyStrategy(self.env).content)

    def test_with_oldcontent(self):
        req = MockRequest(self.env, path_info='/foo')
        FilterSystem(self.env).test(req, 'John Doe', [('Test', 'Test 1 2 3')])
        self.assertEqual('Test 1 2 3', DummyStrategy(self.env).content)

    def test_with_oldcontent_multiline(self):
        req = MockRequest(self.env, path_info='/foo')
        FilterSystem(self.env).test(req, 'John Doe', [('Text\n1 2 3\n7 8 9',
                                                       'Test\n1 2 3\n4 5 6')])
        self.assertEqual('Test\n4 5 6', DummyStrategy(self.env).content)

    def test_bad_karma(self):
        req = MockRequest(self.env, path_info='/foo')
        DummyStrategy(self.env).configure(-5, 'Blacklisted')
        try:
            FilterSystem(self.env).test(req, 'John Doe', [(None, 'Test')])
            self.fail('Expected RejectContent exception')
        except RejectContent, e:
            self.assertEqual('<div class="message">'
                             #'Submission rejected as potential spam '
                             '<ul><li>Blacklisted</li></ul></div>', str(e))

    def test_good_karma(self):
        req = MockRequest(self.env, path_info='/foo')
        DummyStrategy(self.env).configure(5)
        FilterSystem(self.env).test(req, 'John Doe', [(None, 'Test')])

    def test_log_reject(self):
        req = MockRequest(self.env, path_info='/foo')
        DummyStrategy(self.env).configure(-5, 'Blacklisted')
        try:
            FilterSystem(self.env).test(req, 'John Doe', [(None, 'Test')])
            self.fail('Expected RejectContent exception')
        except RejectContent, e:
            pass

        log = list(LogEntry.select(self.env))
        self.assertEqual(1, len(log))
        entry = log[0]
        self.assertEqual('/foo', entry.path)
        self.assertEqual('John Doe', entry.author)
        self.assertEqual(False, entry.authenticated)
        self.assertEqual('127.0.0.1', entry.ipnr)
        self.assertEqual('Test', entry.content)
        self.assertEqual(True, entry.rejected)
        self.assertEqual(-5, entry.karma)
        self.assertEqual([['DummyStrategy', '-5', 'Blacklisted']], entry.reasons)

    def test_log_accept(self):
        req = MockRequest(self.env, path_info='/foo')
        DummyStrategy(self.env).configure(5)
        FilterSystem(self.env).test(req, 'John Doe', [(None, 'Test')])

        log = list(LogEntry.select(self.env))
        self.assertEqual(1, len(log))
        entry = log[0]
        self.assertEqual('/foo', entry.path)
        self.assertEqual('John Doe', entry.author)
        self.assertEqual(False, entry.authenticated)
        self.assertEqual('127.0.0.1', entry.ipnr)
        self.assertEqual('Test', entry.content)
        self.assertEqual(False, entry.rejected)
        self.assertEqual(5, entry.karma)
        self.assertEqual([['DummyStrategy', '5', 'Dummy']], entry.reasons)

    def test_train_spam(self):
        req = MockRequest(self.env, path_info='/foo')
        entry = LogEntry(self.env, time.time(), '/foo', 'john', False,
                         '127.0.0.1', '', 'Test', False, 5, [], req)
        entry.insert()

        FilterSystem(self.env).train(req, entry.id, spam=True)

        strategy = DummyStrategy(self.env)
        self.assertEqual(True, strategy.train_called)
        self.assertEqual('john', strategy.author)
        self.assertEqual('Test', strategy.content)
        self.assertEqual(True, strategy.spam)

        log = list(LogEntry.select(self.env))
        self.assertEqual(1, len(log))
        entry = log[0]
        self.assertEqual(True, entry.rejected)

    def test_train_ham(self):
        req = MockRequest(self.env, path_info='/foo')
        entry = LogEntry(self.env, time.time(), '/foo', 'john', False,
                         '127.0.0.1', '', 'Test', True, -5, [], req)
        entry.insert()
        FilterSystem(self.env).train(req, entry.id, spam=False)

        strategy = DummyStrategy(self.env)
        self.assertEqual(True, strategy.train_called)
        self.assertEqual('john', strategy.author)
        self.assertEqual('Test', strategy.content)
        self.assertEqual(False, strategy.spam)

        log = list(LogEntry.select(self.env))
        self.assertEqual(1, len(log))
        entry = log[0]
        self.assertEqual(False, entry.rejected)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FilterSystemTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
