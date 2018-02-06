from collective.taskqueue.testing import TASK_QUEUE_ZSERVER_FIXTURE
from collective.taskqueue.testing import ZSERVER_FIXTURE
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig
import ftw.events.tests.builders
import ftw.referencewidget.tests.widgets


class EventsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'Products.DateRecurringIndex')
        z2.installProduct(app, 'ftw.simplelayout')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.events:default')


EVENTS_FIXTURE = EventsLayer()
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EVENTS_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.events:functional")


class EventsZserverLayer(PloneSandboxLayer):

    defaultBases = (EVENTS_FIXTURE, PLONE_ZSERVER)


EVENTS_ZSERVER_FIXTURE = EventsZserverLayer()
FUNCTIONAL_ZSERVER_TESTING = FunctionalTesting(
    bases=(EVENTS_ZSERVER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.events:zserverfunctional")


class MopageTriggerLayer(EventsLayer):

    def setUpZope(self, app, configurationContext):
        super(MopageTriggerLayer, self).setUpZope(app, configurationContext)
        xmlconfig.string(
            '''
            <configure xmlns="http://namespaces.zope.org/zope"
                       xmlns:browser="http://namespaces.zope.org/browser">

                <browser:page
                    for="*"
                    name="mopage-stub"
                    class="ftw.events.tests.test_mopage_trigger.MopageAPIStub"
                    permission="zope2.View"
                    />

            </configure>''',
            context=configurationContext)


MOPAGE_TRIGGER_FIXTURE = MopageTriggerLayer()


MOPAGE_TRIGGER_FUNCTIONAL = FunctionalTesting(
    bases=(ZSERVER_FIXTURE,
           TASK_QUEUE_ZSERVER_FIXTURE,
           MOPAGE_TRIGGER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.events:functional:taskqueue")
