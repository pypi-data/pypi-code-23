from ftw.builder import Builder
from ftw.builder import create
from ftw.events.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from Products.CMFPlone.interfaces.syndication import IFeedSettings
import transaction


class TestSyndication(FunctionalTestCase):

    def setUp(self):
        super(TestSyndication, self).setUp()
        self.grant('Manager')

    @browsing
    def test_feed_only_renders_event_pages(self, browser):
        """
        This test makes sure that the standard Plone syndication machinery
        only renders event pages (and not envent listing blocks available
        on the event folder).
        """
        event_folder = create(Builder('event folder')
                              .titled(u'Not relevant in this test'))
        create(Builder('event page')
               .titled(u'My Event')
               .within(event_folder))
        create(Builder('event page')
               .titled(u'Another Event')
               .within(event_folder))
        create(Builder('event listing block')
               .within(event_folder)
               .titled(u'Event listing block'))

        # Enable syndication on the event folder.
        IFeedSettings(event_folder).enabled = True
        transaction.commit()

        browser.login()

        # Make sure only event pages are rendered.
        browser.visit(event_folder, view='atom.xml')
        self.assertEqual(
            ['My Event', 'Another Event'],
            browser.css('entry title').text
        )
