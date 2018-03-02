# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from rer.newsletter.testing import RER_NEWSLETTER_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that rer.newsletter is properly installed."""

    layer = RER_NEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if rer.newsletter is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'rer.newsletter'))

    def test_browserlayer(self):
        """Test that IRerNewsletterLayer is registered."""
        from rer.newsletter.interfaces import (
            IRerNewsletterLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IRerNewsletterLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = RER_NEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['rer.newsletter'])

    def test_product_uninstalled(self):
        """Test if rer.newsletter is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'rer.newsletter'))

    def test_browserlayer_removed(self):
        """Test that IRerNewsletterLayer is removed."""
        from rer.newsletter.interfaces import \
            IRerNewsletterLayer
        from plone.browserlayer import utils
        self.assertNotIn(
           IRerNewsletterLayer,
           utils.registered_layers())
