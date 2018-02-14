# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from collective.archetypes.select2.testing import COLLECTIVE_ARCHETYPES_SELECT2_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.archetypes.select2 is properly installed."""

    layer = COLLECTIVE_ARCHETYPES_SELECT2_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.archetypes.select2 is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.archetypes.select2'))

    def test_browserlayer(self):
        """Test that ICollectiveArchetypesSelect2Layer is registered."""
        from collective.archetypes.select2.interfaces import (
            ICollectiveArchetypesSelect2Layer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveArchetypesSelect2Layer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_ARCHETYPES_SELECT2_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.archetypes.select2'])

    def test_product_uninstalled(self):
        """Test if collective.archetypes.select2 is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.archetypes.select2'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveArchetypesSelect2Layer is removed."""
        from collective.archetypes.select2.interfaces import \
            ICollectiveArchetypesSelect2Layer
        from plone.browserlayer import utils
        self.assertNotIn(ICollectiveArchetypesSelect2Layer, utils.registered_layers())
