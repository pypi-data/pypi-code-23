from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.events.tests import FunctionalTestCase
from ftw.testbrowser import browsing
import transaction


class TestRssView(FunctionalTestCase):

    def setUp(self):
        super(TestRssView, self).setUp()
        self.grant('Manager')

        self.event_folder = create(Builder('event folder')
                                   .titled(u'events'))

        self.event_folder.events.show_rss_link = True
        transaction.commit()

        # Both events have to be in the future, to achieve this we use the
        # current time and add a few days using timedelta.
        now = datetime.now()

        self.event_1 = create(Builder('event page')
                              .titled(u"An event")
                              .having(description=u'This is a test event')
                              .starting(now + timedelta(days=30))
                              .ending(now + timedelta(days=30, hours=5))
                              .within(self.event_folder))

        self.event_2 = create(Builder('event page')
                              .titled(u"A second event")
                              .having(description=u'Another test event')
                              .starting(now + timedelta(days=60))
                              .ending(now + timedelta(days=60, hours=3))
                              .within(self.event_folder))

    @browsing
    def test_rss_button_is_visible(self, browser):
        browser.login().visit(self.event_folder)
        link_to_rss = browser.css('.ftw-events-eventlistingblock .events-rss')

        self.assertEqual(['Subscribe to the RSS feed'],
                         link_to_rss.text)
        self.assertEqual('http://nohost/plone/events/events/events_rss',
                         link_to_rss.first.get('href'))

    @browsing
    def test_rss_feed_structure(self, browser):
        browser.login().visit(self.event_folder.events, view='events_rss')

        self.assertEqual('2.0',
                         browser.css('rss').first.get('version'))
        self.assertEqual(['http://nohost/plone/events/events/events_rss'],
                         browser.css('rss channel > link').text)
        self.assertEqual(['Events - Events Feed'],
                         browser.css('rss channel > description').text)
        self.assertEqual(['An event', 'A second event'],
                         browser.css('rss item title').text)
        self.assertEqual(['http://nohost/plone/events/an-event',
                          'http://nohost/plone/events/a-second-event'],
                         browser.css('rss channel item link').text)
