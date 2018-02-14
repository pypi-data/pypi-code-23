# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.archetypes.select2


class CollectiveArchetypesSelect2Layer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.archetypes.select2)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.archetypes.select2:default')


COLLECTIVE_ARCHETYPES_SELECT2_FIXTURE = CollectiveArchetypesSelect2Layer()


COLLECTIVE_ARCHETYPES_SELECT2_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_ARCHETYPES_SELECT2_FIXTURE,),
    name='CollectiveArchetypesSelect2Layer:IntegrationTesting'
)


COLLECTIVE_ARCHETYPES_SELECT2_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_ARCHETYPES_SELECT2_FIXTURE,),
    name='CollectiveArchetypesSelect2Layer:FunctionalTesting'
)


COLLECTIVE_ARCHETYPES_SELECT2_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_ARCHETYPES_SELECT2_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveArchetypesSelect2Layer:AcceptanceTesting'
)
