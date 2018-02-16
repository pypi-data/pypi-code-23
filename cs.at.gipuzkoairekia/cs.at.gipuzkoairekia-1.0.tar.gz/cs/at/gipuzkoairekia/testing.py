# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import z2

import cs.at.gipuzkoairekia


class CsAtGipuzkoaIrekiaLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        z2.installProduct(app, 'Products.Archetypes')
        z2.installProduct(app, 'Products.ATContentTypes')
        self.loadZCML(package=cs.at.gipuzkoairekia)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'cs.at.gipuzkoairekia:default')
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ['Manager'], [])

        login(portal, SITE_OWNER_NAME)

        if portal.portal_setup.profileExists(
                'Products.ATContentTypes:default'):
            applyProfile(portal, 'Products.ATContentTypes:default')
        if portal.portal_setup.profileExists(
                'plone.app.collection:default'):
            applyProfile(portal, 'plone.app.collection:default')


CS_AT_GIPUZKOAIREKIA_FIXTURE = CsAtGipuzkoaIrekiaLayer()

CS_AT_GIPUZKOAIREKIA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CS_AT_GIPUZKOAIREKIA_FIXTURE,),
    name='CsAtGipuzkoaIrekiaLayer:IntegrationTesting'
)

CS_AT_GIPUZKOAIREKIA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CS_AT_GIPUZKOAIREKIA_FIXTURE, ),
    name='CsAtGipuzkoaIrekiaLayer:FunctionalTesting'
)

CS_AT_GIPUZKOAIREKIA_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        CS_AT_GIPUZKOAIREKIA_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CsAtGipuzkoaIrekiaLayer:AcceptanceTesting'
)
