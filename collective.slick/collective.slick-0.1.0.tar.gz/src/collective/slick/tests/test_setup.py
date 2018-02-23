# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from collective.slick.testing import COLLECTIVE_SLICK_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.slick is properly installed."""

    layer = COLLECTIVE_SLICK_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.slick is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.slick'))

    def test_browserlayer(self):
        """Test that ICollectiveSlickLayer is registered."""
        from collective.slick.interfaces import (
            ICollectiveSlickLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectiveSlickLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_SLICK_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.slick'])

    def test_product_uninstalled(self):
        """Test if collective.slick is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.slick'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveSlickLayer is removed."""
        from collective.slick.interfaces import \
            ICollectiveSlickLayer
        from plone.browserlayer import utils
        self.assertNotIn(
           ICollectiveSlickLayer,
           utils.registered_layers())
