# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.js.tooltipster.testing import COLLECTIVE_JS_TOOLTIPSTER_INTEGRATION_TESTING  # noqa
from plone import api

import unittest2 as unittest


class TestSetup(unittest.TestCase):
    """Test that collective.js.tooltipster is properly installed."""

    layer = COLLECTIVE_JS_TOOLTIPSTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.js.tooltipster is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.js.tooltipster'))

    def test_uninstall(self):
        """Test if collective.js.tooltipster is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.js.tooltipster'])
        self.assertFalse(self.installer.isProductInstalled('collective.js.tooltipster'))

    def test_browserlayer(self):
        """Test that ICollectiveJsTooltipsterLayer is registered."""
        from collective.js.tooltipster.interfaces import ICollectiveJsTooltipsterLayer
        from plone.browserlayer import utils
        self.assertIn(ICollectiveJsTooltipsterLayer, utils.registered_layers())
