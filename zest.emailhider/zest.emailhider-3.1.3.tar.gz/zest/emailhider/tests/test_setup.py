# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from zest.emailhider.testing import ZEST_EMAILHIDER_INTEGRATION_TESTING

import unittest


class TestSetup(unittest.TestCase):
    """Test that zest.emailhider is properly installed."""

    layer = ZEST_EMAILHIDER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if zest.emailhider is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'zest.emailhider'))

    def test_browserlayer(self):
        """Test that IZestEmailhiderLayer is registered."""
        from zest.emailhider.interfaces import (
            IZestEmailHiderLayer)
        from plone.browserlayer import utils
        self.assertIn(IZestEmailHiderLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ZEST_EMAILHIDER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['zest.emailhider'])

    def test_product_uninstalled(self):
        """Test if zest.emailhider is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'zest.emailhider'))
