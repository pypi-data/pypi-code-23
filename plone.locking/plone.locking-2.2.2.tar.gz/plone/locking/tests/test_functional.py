# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.locking.testing import PLONE_LOCKING_FUNCTIONAL_TESTING
from plone.locking.testing import optionflags
from plone.testing import layered
from Products.CMFCore.utils import getToolByName

import doctest
import unittest


doctests = (
    'locking.rst',
)


def add_member(portal, username):
    portal_membership = getToolByName(portal, 'portal_membership')
    portal_membership.addMember(username, 'secret', ('Member', ), [])


def setup(doctest):
    portal = doctest.globs['layer']['portal']
    add_member(portal, 'member1', )
    add_member(portal, 'member2', )

    logout()
    login(portal, 'member1')
    setRoles(portal, 'member1', ['Manager', ])
    portal.invokeFactory('Document', 'doc')
    setRoles(portal, 'member1', ['Member', ])


def test_suite():
    suite = unittest.TestSuite()
    tests = [
        layered(
            doctest.DocFileSuite(
                'tests/{0}'.format(test_file),
                package='plone.locking',
                optionflags=optionflags,
                setUp=setup,
            ),
            layer=PLONE_LOCKING_FUNCTIONAL_TESTING,
        )
        for test_file in doctests
    ]
    suite.addTests(tests)
    return suite

