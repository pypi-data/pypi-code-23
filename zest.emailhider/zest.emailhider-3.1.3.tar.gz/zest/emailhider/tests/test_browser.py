# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone.testing.z2 import Browser
from zest.emailhider.testing import ZEST_EMAILHIDER_FUNCTIONAL_TESTING

import unittest


class TestView(unittest.TestCase):
    """Test that our view is properly working."""

    layer = ZEST_EMAILHIDER_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.browser = Browser(self.layer['app'])

    def test_json_browser(self):
        self.browser.open(
            self.portal.absolute_url() + '/test_emailhider')
        contents = self.browser.contents
        open('/tmp/test.html', 'w').write(self.browser.contents)
        self.assertNotIn('info@example.org', contents)
