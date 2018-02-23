# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.slick


class CollectiveSlickLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.slick)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.slick:default')


COLLECTIVE_SLICK_FIXTURE = CollectiveSlickLayer()


COLLECTIVE_SLICK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_SLICK_FIXTURE,),
    name='CollectiveSlickLayer:IntegrationTesting'
)


COLLECTIVE_SLICK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_SLICK_FIXTURE,),
    name='CollectiveSlickLayer:FunctionalTesting'
)


COLLECTIVE_SLICK_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_SLICK_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveSlickLayer:AcceptanceTesting'
)
