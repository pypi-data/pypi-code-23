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

from trac.core import TracError
from trac.perm import PermissionSystem
from trac.test import EnvironmentStub, MockRequest
from trac.web.api import RequestDone
from trac.wiki.model import WikiPage
from trac.wiki.web_ui import WikiModule

from tracspamfilter.filters import regex
from tracspamfilter.filters.regex import RegexFilterStrategy


class DummyWikiPage(object):

    def __init__(self):
        self.text = ''

    def __call__(self, env, name):
        self.env = env
        self.name = name
        self.exists = True
        return self


class RegexFilterStrategyTestCase(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentStub(enable=['trac.*', RegexFilterStrategy],
                                   default_data=True)
        self.page = regex.WikiPage = DummyWikiPage()
        self.strategy = RegexFilterStrategy(self.env)

    def tearDown(self):
        self.env.reset_db()

    def _dispatch_request(self, req):
        module = WikiModule(self.env)
        self.assertTrue(module.match_request(req))
        try:
            params = module.process_request(req)
        except RequestDone:
            return []
        else:
            return params

    def test_no_patterns(self):
        req = MockRequest(self.env)
        retval = self.strategy.test(req, 'anonymous', 'foobar',
                                    '127.0.0.1')
        self.assertEqual(None, retval)

    def test_one_matching_pattern(self):
        req = MockRequest(self.env)
        self.page.text = """{{{
foobar
}}}"""
        self.strategy.wiki_page_changed(self.page)
        rv = self.strategy.test(req, 'anonymous', 'foobar', '127.0.0.1')
        self.assertEqual((-5, "Content contained these blacklisted "
                              "patterns: %s", '\'foobar\''), rv)

    def test_multiple_matching_pattern(self):
        self.page.text = """{{{
foobar
^foo
bar$
}}}"""
        self.strategy.wiki_page_changed(self.page)
        req = MockRequest(self.env)
        rv = self.strategy.test(req, 'anonymous', '\nfoobar', '127.0.0.1')
        self.assertEqual((-10, "Content contained these blacklisted "
                               "patterns: %s", '\'foobar\', \'bar$\''), rv)

    def test_view_page_with_invalid_pattern(self):
        """Page with invalid pattern should render fine, but not allow
        an edit without correcting the invalid pattern.
        """
        text = """{{{
(?i)eventbrite\.com
(?i)sneaker(?:supplier|nice\.com
}}}"""
        page = WikiPage(self.env)
        page.text = text
        page.name = 'BadContent'
        try:
            page.save('anonymous', 'Page created.')
        except TracError:
            self.assertTrue(WikiPage(self.env, 'BadContent').exists)
        else:
            self.fail("Saving page with invalid content did not "
                      "raise a TracError.")
        req = MockRequest(self.env, authname='user', args={
            'action': 'view',
        }, path_info='/wiki/BadContent')

        data = self._dispatch_request(req)[1]

        self.assertEqual(page.text, data['text'])

        req = MockRequest(self.env, authname='user', args={
            'action': 'edit',
            'preview': True,
            'version': 1,
            'text': text
        }, method='POST', path_info='/wiki/BadContent')
        self._dispatch_request(req)

        self.assertIn('Invalid Wiki page: Error in pattern '
                      '<tt>(?i)sneaker(?:supplier|nice\\.com</tt>: '
                      '<i>unbalanced parenthesis</i>.',
                      req.chrome['warnings'])

    def test_save_page_with_invalid_pattern(self):
        """Page cannot be saved with an invalid pattern."""
        perm = PermissionSystem(self.env)
        perm.grant_permission('user', 'authenticated')
        text = """{{{
        (?i)eventbrite\.com
        (?i)sneaker(?:supplier|nice\.com
        }}}"""
        req = MockRequest(self.env, authname='user', args={
            'action': 'edit',
            'text': text,
            'version': 0,
        }, method='POST', path_info='/wiki/BadContent')

        self._dispatch_request(req)

        self.assertIn('Invalid Wiki page: Error in pattern '
                      '<tt>(?i)sneaker(?:supplier|nice\\.com</tt>: '
                      '<i>unbalanced parenthesis</i>.',
                      req.chrome['warnings'])

    def test_save_page_with_valid_patterns(self):
        """Page with valid patterns can be saved."""
        perm = PermissionSystem(self.env)
        perm.grant_permission('user', 'authenticated')
        text = """{{{
        (?i)eventbrite\.com
        (?i)sneaker(?:supplier|nice)\.com
        }}}"""
        req = MockRequest(self.env, authname='user', args={
            'action': 'edit',
            'text': text,
            'version': 0,
        }, method='POST', path_info='/wiki/BadContent')

        self._dispatch_request(req)

        self.assertIn('Your changes have been saved in version 1',
                      unicode(req.chrome['notices']))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RegexFilterStrategyTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
