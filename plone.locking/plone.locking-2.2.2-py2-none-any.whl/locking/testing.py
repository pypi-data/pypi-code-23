# -*- coding: utf-8 -*-
from plone.app.testing import applyProfile
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting

import doctest


class PloneLockingLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        import plone.locking
        self.loadZCML(package=plone.locking)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.contenttypes:default')


PLONE_LOCKING_FIXTURE = PloneLockingLayer()

PLONE_LOCKING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_LOCKING_FIXTURE,),
    name='PloneLockingLayer:Integration',
)

PLONE_LOCKING_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_LOCKING_FIXTURE,),
    name='PloneLockingLayer:Functional',
)

optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE
    | doctest.ELLIPSIS
    | doctest.NORMALIZE_WHITESPACE
)
