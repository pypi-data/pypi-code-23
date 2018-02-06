from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.events.tests import FunctionalTestCase
from ftw.events.tests.utils import enable_behavior
from ftw.testbrowser import browsing
from ftw.testing import freeze
from plone import api


class TestEventListing(FunctionalTestCase):

    def setUp(self):
        super(TestEventListing, self).setUp()
        self.grant('Manager')

    @browsing
    def test_event_listing(self, browser):
        """
        This test makes sure the event listing view renders the events.
        """
        event_folder = create(Builder('event folder')
                              .titled(u'Not relevant in this test'))
        create(Builder('event page')
               .titled(u'My Event')
               .within(event_folder))

        browser.login()

        # Get the event folder's event listing block which has been created
        # automatically.
        block = api.content.find(
            portal_type='ftw.events.EventListingBlock',
            within=event_folder
        )[0].getObject()

        # Make sure the view renders the events.
        browser.visit(block, view='@@events')
        self.assertEqual(
            ['My Event'],
            browser.css('.event-row .title').text
        )

    @browsing
    def test_custom_event_listing_title(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'Not relevant in this test'))
        event_folder = create(Builder('event folder')
                              .titled(u'Not relevant in this test')
                              .within(page))
        create(Builder('event page')
               .titled(u'Not relevant in this test')
               .within(event_folder))
        block = create(Builder('event listing block')
                       .within(page)
                       .titled(u'Not relevant in this test'))

        browser.login()

        # A fallback title must be rendered on the view by default.
        browser.visit(block, view='@@events')
        self.assertEqual(
            ['Events'],
            browser.css('.documentFirstHeading').text
        )

        # Configure a custom title.
        browser.login().visit(block, view='edit.json')
        response = browser.json
        browser.parse(response['content'])
        browser.fill({
            'Title of the view behind the "more items" link': u'All my events',
        })
        browser.find_button_by_label('Save').click()

        # Now the view must render the custom title.
        browser.visit(block, view='@@events')
        self.assertEqual(
            ['All my events'],
            browser.css('.documentFirstHeading').text
        )

    @browsing
    def test_event_listing_renders_location(self, browser):
        event_folder = create(Builder('event folder'))
        event = create(Builder('event page')
                       .titled(u'My Event')
                       .having(location_title='Infinite Loop 1',
                               location_street='Hamburgstrasse 3743x',
                               location_zip='12345',
                               location_city='Hamburg')
                       .within(event_folder))
        browser.login()

        # Get the event folder's event listing block which has been created
        # automatically.
        block = api.content.find(
            portal_type='ftw.events.EventListingBlock',
            within=event_folder
        )[0].getObject()

        # Make sure the location is rendered.
        browser.visit(block, view='@@events')
        self.assertEqual(
            ['Infinite Loop 1, Hamburgstrasse 3743x, 12345 Hamburg'],
            browser.css('.event-row .byline .location').text
        )

        # Empty the location and make sure it is no longer rendered.
        browser.visit(event, view='edit')
        browser.fill({'Location: title': u'',
                      'Location: street and number': u'',
                      'Location: ZIP code': u'',
                      'Location: city': u''}).submit()
        browser.visit(block, view='@@events')
        self.assertEqual(
            [],
            browser.css('.event-row .byline .location')
        )

    @browsing
    def test_contributor_can_see_inactive_events_in_event_listing_view(self, browser):
        enable_behavior('plone.app.dexterity.behaviors.metadata.IPublication', 'ftw.events.EventPage')

        event_folder = create(Builder('event folder'))
        create(Builder('event page')
               .titled(u'Future Event')
               .within(event_folder)
               .having(effective=datetime.now() + timedelta(days=10)))

        # Get the event folder's event listing block which has been created
        # automatically.
        block = api.content.find(
            portal_type='ftw.events.EventListingBlock',
            within=event_folder
        )[0].getObject()

        # Make sure an editor can see inactive events.
        contributor = create(Builder('user').named('A', 'Contributor').with_roles('Contributor'))
        browser.login(contributor).visit(block, view='@@events')
        self.assertEqual(
            ['Future Event'],
            browser.css('.event-row .title').text
        )

        # Make sure an anonymous user does not see the inactive news.
        browser.logout().visit(block, view='@@events')
        self.assertEqual(
            [],
            browser.css('.event-row .title').text
        )

    @browsing
    def test_listing_does_not_render_past_events(self, browser):
        page = create(Builder('sl content page'))
        event_folder = create(Builder('event folder')
                              .titled(u'Event Folder')
                              .within(page))
        create(Builder('event listing block')
               .within(page)
               .titled(u'Event listing block')
               .having(show_more_items_link=True,
                       exclude_past_events=True))

        with freeze(datetime(2010, 7, 1, 15, 0, 0)):
            create(Builder('event page')
                   .titled(u'Past event')
                   .starting(datetime(2010, 1, 1))
                   .ending(datetime(2010, 1, 1))
                   .within(event_folder))
            create(Builder('event page')
                   .titled(u'Today event')
                   .starting(datetime(2010, 7, 1, 12, 0, 0))
                   .ending(datetime(2010, 7, 1, 18, 0, 0))
                   .within(event_folder))
            create(Builder('event page')
                   .titled(u'Future event')
                   .starting(datetime(2010, 7, 2))
                   .ending(datetime(2010, 7, 2))
                   .within(event_folder))
            create(Builder('event page')
                   .titled(u'Event which ended a few hours ago')
                   .starting(datetime(2010, 7, 1, 9, 0, 0))
                   .ending(datetime(2010, 7, 1, 14, 0, 0))
                   .within(event_folder))

            browser.login().visit(page)
            browser.css('a.event-listingblock-moreitemslink').first.click()
            self.assertEqual(
                ['Event which ended a few hours ago',
                 'Today event',
                 'Future event'],
                browser.css('.event-item h3.title').text
            )
