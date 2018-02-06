from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.events.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages


class TestEventPage(FunctionalTestCase):

    @browsing
    def test_create_event_page(self, browser):
        self.grant('Manager')
        folder = create(Builder('event folder').titled(u'Activities'))
        browser.login().open(folder)
        factoriesmenu.add('Event Page')

        browser.fill({'Title': 'Jogging'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals('http://nohost/plone/activities/jogging/view',
                          browser.url)

    @browsing
    def test_event_details_WHEN_shows_dates(self, browser):
        self.grant('Manager')
        folder = create(Builder('event folder'))
        event = create(Builder('event page')
                       .starting(datetime(2013, 10, 7, 9, 00))
                       .ending(datetime(2013, 10, 7, 16, 00))
                       .having(recurrence='RRULE:FREQ=DAILY;COUNT=4')
                       .within(folder))

        browser.login().open(event)
        self.assertEquals(['Oct 07, 2013 from 09:00 AM to 04:00 PM',
                           'Oct 08, 2013 from 09:00 AM to 04:00 PM',
                           'Oct 09, 2013 from 09:00 AM to 04:00 PM',
                           'Oct 10, 2013 from 09:00 AM to 04:00 PM'],
                          browser.css('.event-details .when li').text)

    @browsing
    def test_event_details_shows_location(self, browser):
        self.grant('Manager')
        folder = create(Builder('event folder'))
        event = create(Builder('event page')
                       .having(location_title='Infinite Loop 1')
                       .within(folder))

        browser.login().open(event)
        self.assertEqual(
            ['Infinite Loop 1'],
            browser.css('.event-details .location p').text
        )
