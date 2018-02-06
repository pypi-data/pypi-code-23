from datetime import datetime
from DateTime import DateTime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.events.behaviors.mopage import IMopageModificationDate
from ftw.events.tests import FunctionalTestCase
from ftw.events.tests import utils
from ftw.events.tests import XMLDiffTestCase
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from ftw.testing import freeze
from ftw.testing import staticuid
from path import Path
from plone.app.textfield import RichTextValue
from pytz import timezone
import re


ZURICH = timezone('Europe/Zurich')


class TestMopageExport(FunctionalTestCase, XMLDiffTestCase):

    @staticuid('uid')
    @browsing
    def test_01_export_events(self, browser):
        self.grant('Manager')
        event_folder = create(Builder('event folder').titled(u'event folder'))

        with freeze(datetime(2010, 3, 14, 20, 18, tzinfo=ZURICH)):
            events1 = create(
                Builder('event page')
                .titled(u'Wanderausstellung Kaffeebohnen')
                .within(event_folder)
                .starting(datetime(2010, 10, 7, 9, 00))
                .ending(datetime(2010, 10, 7, 16, 00))
                .having(recurrence='RRULE:FREQ=DAILY;COUNT=4',
                        description=u'Die Wanderausstellung Kaffeebohnen'
                        u' besch\xe4ftigt sich mit allen m\xf6glichen'
                        u' Kaffeesorten aus aller Welt.',
                        subjects=('Kaffee', 'Wanderausstellung'),
                        location_title='Kunstmuseum Bern',
                        location_street='Hodlerstrasse 8',
                        location_zip='3011',
                        location_city='Bern'))

            lorem = RichTextValue(self.asset('lorem1.html'))
            block = create(Builder('sl textblock').within(events1)
                           .with_dummy_image()
                           .having(text=lorem))
            utils.create_page_state(events1, block)
            IMopageModificationDate(events1).set_date(DateTime('2010/3/15'))

        with freeze(datetime(2010, 5, 17, 15, 34, tzinfo=ZURICH)):
            create(Builder('event page')
                   .titled(u'Bratwurstgrillieren')
                   .within(event_folder)
                   .starting(datetime(2010, 5, 18))
                   .ending(datetime(2010, 5, 18))
                   .having(whole_day=True,
                           # Location is incomplete and will not appear.
                           location_title='Kunstmuseum Bern'))

        with freeze(datetime(2011, 1, 2, 3, 4, tzinfo=ZURICH)):
            self.assert_mopage_export('mopage.events.xml', event_folder)

    @browsing
    def test_pagination(self, browser):
        self.grant('Manager')
        event_folder = create(Builder('event folder').titled(u'Events'))
        with freeze(datetime(2015, 10, 1, 14, 0, tzinfo=ZURICH)) as clock:
            create(Builder('event page').titled(u'One').within(event_folder)
                   .starting(datetime.now() + timedelta(hours=2))
                   .ending(datetime.now() + timedelta(hours=2)))
            clock.forward(days=1)
            create(Builder('event page').titled(u'Two').within(event_folder)
                   .starting(datetime.now() + timedelta(hours=2))
                   .ending(datetime.now() + timedelta(hours=2)))
            clock.forward(days=1)
            create(Builder('event page').titled(u'Three').within(event_folder)
                   .starting(datetime.now() + timedelta(hours=2))
                   .ending(datetime.now() + timedelta(hours=2)))
            clock.forward(days=1)
            create(Builder('event page').titled(u'Four').within(event_folder)
                   .starting(datetime.now() + timedelta(hours=2))
                   .ending(datetime.now() + timedelta(hours=2)))
            clock.forward(days=1)
            create(Builder('event page').titled(u'Five').within(event_folder)
                   .starting(datetime.now() + timedelta(hours=2))
                   .ending(datetime.now() + timedelta(hours=2)))

        browser.open(event_folder, view='mopage.events.xml?per_page=2')
        self.assert_events_in_browser(['Five', 'Four'])
        links = self.get_links_from_response()
        self.assertEquals(
            {'next': 'http://nohost/plone/events/mopage.events.xml?per_page=2&page=2',
             'last': 'http://nohost/plone/events/mopage.events.xml?per_page=2&page=3'},
            links)

        browser.open(links['next'])
        self.assert_events_in_browser(['Three', 'Two'])
        links = self.get_links_from_response()
        self.assertEquals(
            {'first': 'http://nohost/plone/events/mopage.events.xml?per_page=2&page=1',
             'prev': 'http://nohost/plone/events/mopage.events.xml?per_page=2&page=1',
             'next': 'http://nohost/plone/events/mopage.events.xml?per_page=2&page=3',
             'last': 'http://nohost/plone/events/mopage.events.xml?per_page=2&page=3'},
            links)

        browser.open(links['next'])
        self.assert_events_in_browser(['One'])
        links = self.get_links_from_response()
        self.assertEquals(
            {'first': 'http://nohost/plone/events/mopage.events.xml?per_page=2&page=1',
             'prev': 'http://nohost/plone/events/mopage.events.xml?per_page=2&page=2'},
            links)

    @browsing
    def test_export_all_events_on_site(self, browser):
        self.grant('Manager')
        create(Builder('event page').titled(u'One').within(
            create(Builder('event folder').titled(u'Event Folder One'))))
        create(Builder('event page').titled(u'Two').within(
            create(Builder('event folder').titled(u'Event Folder Two'))))

        browser.open(self.portal, view='mopage.events.xml')
        self.assert_events_in_browser(['One', 'Two'])

    @browsing
    def test_title_is_cropped(self, browser):
        self.grant('Manager')
        create(Builder('event page').titled(u'A' * 150).within(
            create(Builder('event folder'))))

        browser.open(self.portal, view='mopage.events.xml')
        self.assert_events_in_browser(['A' * 95 + ' ...'])

    @browsing
    def test_include_root_arguments_when_submitted_as_GET_param(self, browser):
        self.grant('Manager')
        create(Builder('event page').within(create(Builder('event folder'))))

        with freeze(datetime(2016, 8, 9, 21, 45, tzinfo=ZURICH)):
            browser.open(self.portal, view='mopage.events.xml',
                         data={'partner': 'Partner',
                               'partnerid': '123',
                               'passwort': 's3c>r3t',
                               'importid': '456',
                               'vaterobjekt': 'xy',
                               'unkown_key': 'should not appear'})

        self.assertEquals(
            {
                'export_time': '2016-08-09 22:45:00',
                'partner': 'Partner',
                'partnerid': '123',
                'passwort': 's3c>r3t',
                'importid': '456',
                'vaterobjekt': 'xy',
            },
            browser.css('import').first.attrib)

    def assert_mopage_export(self, asset_name, export_context):
        expected = self.asset(asset_name)
        browser.open(export_context, view='mopage.events.xml')
        got = browser.contents
        # replace dynamic scale image urls for having static test results:
        got = re.sub(r'\/@@images/[a-z0-9-]{36}.jpeg', '/image.jpg', got)
        # remove trailing spaces:
        got = re.sub(r' +$', '', got, flags=re.M)
        self.maxDiff = None
        self.assert_xml(expected, got)

    def asset(self, asset_name):
        assets = Path(__file__).joinpath('..', 'mopage_assets').abspath()
        return assets.joinpath(asset_name).bytes()

    def assert_events_in_browser(self, expected_titles):
        got_titles = browser.css('titel').text
        self.assertEquals(expected_titles, got_titles)

    def get_links_from_response(self):
        def parse_link(text):
            return tuple(reversed(re.match(
                r'^<([^>]+)>; rel="([^"]+)"', text).groups()))

        return dict(map(parse_link, browser.headers.get('Link').split(',')))
