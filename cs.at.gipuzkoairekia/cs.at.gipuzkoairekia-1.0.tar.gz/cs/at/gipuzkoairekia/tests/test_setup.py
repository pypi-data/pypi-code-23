# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from cs.at.gipuzkoairekia.testing import CS_AT_GIPUZKOAIREKIA_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that cs.at.gipuzkoairekia is properly installed."""

    layer = CS_AT_GIPUZKOAIREKIA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if cs.at.gipuzkoairekia is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'cs.at.gipuzkoairekia'))

    def test_browserlayer(self):
        """Test that I{{{ package.browserlayer }}} is registered."""
        from cs.at.gipuzkoairekia.interfaces import (
            ICsAtGipuzkoaIrekia)
        from plone.browserlayer import utils
        self.assertIn(
            ICsAtGipuzkoaIrekia,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = CS_AT_GIPUZKOAIREKIA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get(userid=TEST_USER_ID).getRoles()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['cs.at.gipuzkoairekia'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if cs.at.gipuzkoairekia is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'cs.at.gipuzkoairekia'))

    def test_browserlayer_removed(self):
        """Test that ICsAtGipuzkoaIrekia is removed."""
        from cs.at.gipuzkoairekia.interfaces import \
            ICsAtGipuzkoaIrekia
        from plone.browserlayer import utils
        self.assertNotIn(ICsAtGipuzkoaIrekia, utils.registered_layers())
