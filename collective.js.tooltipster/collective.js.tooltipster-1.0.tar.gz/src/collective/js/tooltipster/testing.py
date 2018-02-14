# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer
from plone.testing import z2

import collective.js.tooltipster


COLLECTIVE_JS_TOOLTIPSTER_FIXTURE = PloneWithPackageLayer(
    zcml_package=collective.js.tooltipster,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.js.tooltipster:testing',
    name='CollectiveJsTooltipsterLayer',
    additional_z2_products=()
)


COLLECTIVE_JS_TOOLTIPSTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_JS_TOOLTIPSTER_FIXTURE,),
    name='CollectiveJsTooltipsterLayer:IntegrationTesting'
)


COLLECTIVE_JS_TOOLTIPSTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_JS_TOOLTIPSTER_FIXTURE,),
    name='CollectiveJsTooltipsterLayer:FunctionalTesting'
)


COLLECTIVE_JS_TOOLTIPSTER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_JS_TOOLTIPSTER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveJsTooltipsterLayer:AcceptanceTesting'
)
