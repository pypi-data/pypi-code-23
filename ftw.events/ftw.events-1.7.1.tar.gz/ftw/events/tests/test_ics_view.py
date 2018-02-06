from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.events.tests import RealFuncitionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_REQUESTS


class TestIsICSView(RealFuncitionalTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.grant('Manager')
        self.folder = create(Builder('event folder').titled(u'Activities'))

        self.event = create(Builder('event page')
                            .titled(u"A Event")
                            .starting(datetime(2013, 10, 7, 9, 00))
                            .ending(datetime(2013, 10, 7, 16, 00))
                            .having(recurrence='RRULE:FREQ=DAILY;COUNT=4')
                            .within(self.folder))

    @browsing
    def test_ics_view_is_ics(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.login().visit(self.event, view="ics_view")

        body = browser.contents
        self.assertIn('SUMMARY:A Event', body)
        self.assertIn('BEGIN:VCALENDAR', body)
        self.assertIn('BEGIN:VEVENT', body)
        self.assertIn('END:VCALENDAR', body)
        self.assertIn('END:VEVENT', body)
