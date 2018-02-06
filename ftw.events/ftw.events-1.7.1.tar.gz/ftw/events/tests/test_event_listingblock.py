import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.events.tests import FunctionalTestCase
from ftw.events.tests.utils import enable_behavior
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from Products.CMFPlone.interfaces.syndication import IFeedSettings


class TestEventListingBlock(FunctionalTestCase):

    def setUp(self):
        super(TestEventListingBlock, self).setUp()
        self.grant('Manager')

    def _get_event_titles_from_block(self, browser):
        """
        This helper method returns the titles of the events rendered
        in the event listing block. Use this method in the test case to
        make sure the block lists only the events we want it to.
        """
        return browser.css('.ftw-events-eventlistingblock .event-row h3.title').text

    @browsing
    def test_event_listing_block_builder(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))

        create(Builder('event listing block')
               .within(page)
               .titled(u'This block renders event pages'))

        browser.login().visit(page)
        self.assertEqual(
            ['This block renders event pages'],
            browser.css('.sl-block.ftw-events-eventlistingblock h2').text
        )

    @browsing
    def test_event_listing_block_can_be_added_on_contentpage(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))
        browser.login().visit(page)

        factoriesmenu.add('EventListingBlock')
        browser.fill({
            'Title': u'This block renders event pages',
        }).save()

        browser.open(page)
        self.assertEqual(
            ['This block renders event pages'],
            browser.css('.sl-block.ftw-events-eventlistingblock h2').text
        )

    @browsing
    def test_event_listing_block_does_not_render_title(self, browser):
        page = create(Builder('sl content page').titled(u'A page'))

        block = create(Builder('event listing block')
                       .within(page)
                       .titled(u'This block renders event pages'))
        browser.login()

        # Make sure the title is rendered by default.
        browser.visit(page)
        self.assertEqual(
            ['This block renders event pages'],
            browser.css('.sl-block.ftw-events-eventlistingblock h2').text
        )

        # Tell the block to no longer display the title.
        browser.login().visit(block, view='edit.json')
        response = browser.json
        browser.parse(response['content'])
        browser.fill({
            'Show title': False,
        })
        browser.find_button_by_label('Save').click()

        # Make sure the title is no longer rendered.
        browser.visit(page)
        self.assertEqual(
            [],
            browser.css('.sl-block.ftw-events-eventlistingblock h2')
        )

    @browsing
    def test_sort_order(self, browser):
        """
        This test makes sure that the events are sorted in ascending order by
        their start date.
        """
        event_folder = create(Builder('event folder').titled(u'Event Folder'))
        with freeze(datetime.datetime(2010, 7, 1)):
            create(Builder('event page')
                   .titled(u'Event of Hans')
                   .starting(datetime.datetime(2010, 7, 2))
                   .ending(datetime.datetime(2010, 7, 3))
                   .within(event_folder))
            create(Builder('event page')
                   .titled(u'Event of Peter')
                   .starting(datetime.datetime(2010, 7, 1))
                   .ending(datetime.datetime(2010, 7, 5))
                   .within(event_folder))

            browser.login()

            # Make sure that the events are sorted in ascending order.
            browser.visit(event_folder)
            self.assertEqual(
                ['Event of Peter', 'Event of Hans'],
                self._get_event_titles_from_block(browser),
                "Event of Peter must be listed before the event of Hans"
            )

            # Folder listing still renders the items in the order they were added by.
            browser.visit(event_folder, view='folder_contents')
            self.assertEqual(
                ['Event of Hans', 'Event of Peter'],
                browser.css('table#listing-table tr td a.contenttype-ftw-events-eventpage').text
            )

    @browsing
    def test_block_filters_by_path(self, browser):
        """
        This test makes sure that the block only renders items
        from the given path.
        """
        event_folder1 = create(Builder('event folder')
                               .titled(u'Event Folder 1')
                               .within(self.portal))
        create(Builder('event page').titled(u'Hello World 1').within(event_folder1))

        event_folder2 = create(Builder('event folder')
                               .titled(u'Event Folder 2')
                               .within(self.portal))
        create(Builder('event page').titled(u'Hello World 2').within(event_folder2))

        # Prepare a page containing an event listing block.
        page = create(Builder('sl content page').titled(u'Content Page with Eventlistingblock'))
        block = create(Builder('event listing block')
                       .within(page)
                       .having(current_context=False)
                       .titled(u'Not relevant in this test'))

        browser.login()

        # Edit the block and set a path (not possible with builder).
        browser.visit(block, view='edit.json')
        response = browser.json
        browser.parse(response['content'])
        browser.fill({
            'Limit to path': event_folder2,
        })
        browser.find_button_by_label('Save').click()
        browser.visit(page)

        # Make sure the block only lists events from the path
        # we have configured on the block.
        self.assertEqual(
            ['Hello World 2'],
            self._get_event_titles_from_block(browser)
        )

    @browsing
    def test_block_prevents_path_and_current_context(self, browser):
        """
        This test makes sure that a block cannot be configured to
        have a "filter by path" and a "filter by current context" at the
        same time.
        """
        event_folder = create(Builder('event folder').titled(u'Event Folder'))

        browser.login()

        # Note that a default event listing block is created
        # automatically in the event folder. Let's get the block.
        block = event_folder.listFolderContents(
            contentFilter={'portal_type': 'ftw.events.EventListingBlock'}
        )[0]

        # Edit the existing block.
        browser.visit(block, view='edit.json')
        response = browser.json
        browser.parse(response['content'])
        browser.fill({
            'Title': u'Not relevant for this test',
            'Limit to path': '/'.join(event_folder.getPhysicalPath()),
            'Limit to current context': True,
        })
        browser.find_button_by_label('Save').click()
        response = browser.json
        browser.parse(response['content'])

        # Make sure that the form refuses to save.
        self.assertEqual(
            ['There were some errors.'],
            statusmessages.error_messages()
        )
        self.assertIn(
            'You cannot filter by path and current context at the same time.',
            browser.css('.error').text
        )

    @browsing
    def test_block_filter_by_current_context(self, browser):
        """
        This test makes sure the block filters by the current context.
        """
        page1 = create(Builder('sl content page').titled(u'Content Page 1'))
        event_folder1 = create(Builder('event folder')
                               .titled(u'Event Folder 1')
                               .within(page1))
        create(Builder('event page').titled(u'Hello World 1').within(event_folder1))

        page2 = create(Builder('sl content page').titled(u'Content Page 2'))
        event_folder2 = create(Builder('event folder')
                               .titled(u'Event Folder 2')
                               .within(page2))
        create(Builder('event page').titled(u'Hello World 2').within(event_folder2))

        block = create(Builder('event listing block')
                       .within(page2)
                       .titled(u'Not relevant for this test'))

        browser.login()

        # Make sure that the filter by context is active by default.
        browser.visit(page2)
        self.assertEqual(
            ['Hello World 2'],
            self._get_event_titles_from_block(browser),
        )

        # Tell the block to no longer filter by the current context.
        browser.login().visit(block, view='edit.json')
        response = browser.json
        browser.parse(response['content'])
        browser.fill({
            'Limit to current context': False,
        })
        browser.find_button_by_label('Save').click()

        # Make sure the title is no longer rendered.
        browser.visit(page2)
        self.assertEqual(
            ['Hello World 1', 'Hello World 2'],
            self._get_event_titles_from_block(browser),
        )

    @browsing
    def test_block_crops_description(self, browser):
        """
        This test makes sure that the block crops the description of the event
        page to the default length (note that the description is shown by default
        but can be disabled).
        """
        page = create(Builder('sl content page').titled(u'Content Page 1'))
        event_folder = create(Builder('event folder').titled(u'Event Folder 1').within(page))
        create(Builder('event page')
               .titled(u'Hello World 1')
               .having(description=u"This description must be longer than "
                                   u"50 characters so we are able to test "
                                   u"if it will be cropped.")
               .within(event_folder))
        create(Builder('event listing block')
               .within(page)
               .titled(u'This is a EventListingBlock'))

        browser.login().visit(page)
        self.assertEqual(
            ['This description must be longer than 50 ...'],
            browser.css('.sl-block.ftw-events-eventlistingblock .description').text
        )

    @browsing
    def test_block_renders_entire_description(self, browser):
        """
        This test makes sure that the block renders the entire description
        if configured to do so.
        """
        page = create(Builder('sl content page').titled(u'Content Page 1'))
        event_folder = create(Builder('event folder').titled(u'Event Folder 1').within(page))
        create(Builder('event page')
               .titled(u'Hello World 1')
               .having(description=u"This description must be longer than "
                                   u"50 characters so we are able to test "
                                   u"if it will be cropped.")
               .within(event_folder))
        create(Builder('event listing block')
               .within(page)
               .having(description_length=0)
               .titled(u'This is a EventListingBlock'))

        browser.login().visit(page)
        self.assertEqual(
            [
                'This description must be longer than 50 characters '
                'so we are able to test if it will be cropped.'
            ],
            browser.css('.sl-block.ftw-events-eventlistingblock .description').text
        )

    @browsing
    def test_block_does_not_render_description(self, browser):
        """
        This test makes sure that the block does not render the description
        if configured to do so.
        """
        page = create(Builder('sl content page').titled(u'Content Page'))
        event_folder = create(Builder('event folder').titled(u'Event Folder').within(page))
        create(Builder('event page')
               .titled(u'Hello World')
               .having(description=u"The description.")
               .within(event_folder))
        create(Builder('event listing block')
               .within(page)
               .having(show_description=False)
               .titled(u'This is a EventListingBlock'))

        browser.login().visit(page)
        self.assertEqual(
            [],
            browser.css('.sl-block.ftw-events-eventlistingblock .description').text
        )

    @browsing
    def test_block_filters_by_subject(self, browser):
        """
        This test makes sure that the block filters event pages by subject.
        """
        page = create(Builder('sl content page').titled(u'Content Page'))
        event_folder = create(Builder('event folder').titled(u'Event Folder').within(page))
        create(Builder('event listing block')
               .within(page)
               .having(subjects=[u'H\xe4ns'])
               .titled(u'This is a EventListingBlock'))
        with freeze(datetime.datetime(2010, 7, 1)):
            create(Builder('event page')
                   .titled(u'Event of Hans')
                   .having(subjects=[u'H\xe4ns'])
                   .starting(datetime.datetime(2010, 7, 2))
                   .ending(datetime.datetime(2010, 7, 2))
                   .within(event_folder))
            create(Builder('event page')
                   .titled(u'Event of Peter')
                   .having(subjects=['Peter'])
                   .starting(datetime.datetime(2010, 7, 2))
                   .ending(datetime.datetime(2010, 7, 2))
                   .within(event_folder))

            browser.login()
            browser.visit(page)
            self.assertEqual(
                ['Event of Hans'],
                self._get_event_titles_from_block(browser)
            )

    @browsing
    def test_block_limits_quantity(self, browser):
        page = create(Builder('sl content page').titled(u'Content Page'))
        event_folder = create(Builder('event folder').titled(u'Event Folder').within(page))
        quantity = 1
        create(Builder('event listing block')
               .within(page)
               .having(quantity=quantity)
               .having(show_title=False)
               .titled(u'This is a EventListingBlock'))

        with freeze(datetime.datetime(2010, 7, 1)):
            create(Builder('event page')
                   .titled(u'Event of Hans')
                   .starting(datetime.datetime(2010, 7, 2))
                   .ending(datetime.datetime(2010, 7, 2))
                   .within(event_folder))
            create(Builder('event page')
                   .titled(u'Event of Peter')
                   .starting(datetime.datetime(2010, 7, 2))
                   .ending(datetime.datetime(2010, 7, 2))
                   .within(event_folder))

            browser.login()
            browser.visit(page)
            self.assertEqual(
                quantity,
                len(self._get_event_titles_from_block(browser))
            )

    @browsing
    def test_block_renders_link_to_more_items(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'Content Page'))
        event_folder = create(Builder('event folder').
                              titled(u'Event Folder')
                              .within(page))
        create(Builder('event page')
               .titled(u'Event')
               .within(event_folder))
        block = create(Builder('event listing block')
                       .within(page)
                       .having(show_more_items_link=True)
                       .titled(u'This is a EventListingBlock'))

        browser.login()

        # Make sure the link is there.
        browser.visit(page)
        self.assertEqual(
            'http://nohost/plone/content-page/this-is-a-eventlistingblock/events',
            browser.find('More Items').attrib['href']
        )

        # Tell the block to no longer render the link
        browser.login().visit(block, view='edit.json')
        response = browser.json
        browser.parse(response['content'])
        browser.fill({
            'Show link to more items': False,
        })
        browser.find_button_by_label('Save').click()

        # Make sure the link is no longer there.
        browser.visit(page)
        self.assertIsNone(browser.find('More Items'))

    @browsing
    def test_block_renders_link_to_more_items_with_custom_label(self, browser):
        """
        This test makes sure that the link to thew view which renders more items
        has a custom label.
        """
        page = create(Builder('sl content page')
                      .titled(u'Content Page'))
        event_folder = create(Builder('event folder').
                              titled(u'Event Folder')
                              .within(page))
        create(Builder('event page')
               .titled(u'Event')
               .within(event_folder))
        create(Builder('event listing block')
               .within(page)
               .having(show_more_items_link=True)
               .having(more_items_link_label=u'Show me more')
               .titled(u'This is a EventListingBlock'))

        browser.login()

        # Make sure the link is there.
        browser.visit(page)
        self.assertEqual(
            'http://nohost/plone/content-page/this-is-a-eventlistingblock/events',
            browser.find('Show me more').attrib['href']
        )

    def test_syndication_is_enabled_by_default_on_block(self):
        folder = create(Builder('event folder'))

        # Note that a default event listing block is created
        # automatically in the event folder.
        block = folder.listFolderContents(
            contentFilter={'portal_type': 'ftw.events.EventListingBlock'}
        )[0]

        self.assertTrue(
            IFeedSettings(block).enabled
        )
        self.assertEqual(
            ('RSS', 'rss.xml', 'atom.xml'),
            IFeedSettings(block).feed_types
        )

    @browsing
    def test_block_renders_location(self, browser):
        event_folder = create(Builder('event folder'))
        event = create(Builder('event page')
                       .titled(u'My Event')
                       .having(location_title='Infinite Loop 1')
                       .within(event_folder))
        browser.login()

        # Make sure the location is rendered.
        browser.open(event_folder)
        self.assertEqual(
            ['Infinite Loop 1'],
            browser.css('.event-row .byline .location').text
        )

        # Empty the location and make sure it is no longer rendered.
        browser.visit(event, view='edit')
        browser.fill({'Location: title': u''}).submit()
        browser.open(event_folder)
        self.assertEqual(
            [],
            browser.css('.event-row .byline .location')
        )

    @browsing
    def test_block_does_not_render_past_events(self, browser):
        page = create(Builder('sl content page'))
        event_folder = create(Builder('event folder').titled(u'Event Folder').within(page))
        create(Builder('event listing block')
               .within(page)
               .titled(u'Event listing block'))

        with freeze(datetime.datetime(2010, 7, 1, 15, 0, 0)):
            create(Builder('event page')
                   .titled(u'Past event')
                   .starting(datetime.datetime(2010, 1, 1))
                   .ending(datetime.datetime(2010, 1, 1))
                   .within(event_folder))
            create(Builder('event page')
                   .titled(u'Today event')
                   .starting(datetime.datetime(2010, 7, 1, 12, 0, 0))
                   .ending(datetime.datetime(2010, 7, 1, 18, 0, 0))
                   .within(event_folder))
            create(Builder('event page')
                   .titled(u'Future event')
                   .starting(datetime.datetime(2010, 7, 2))
                   .ending(datetime.datetime(2010, 7, 2))
                   .within(event_folder))
            create(Builder('event page')
                   .titled(u'Event which ended a few hours ago')
                   .starting(datetime.datetime(2010, 7, 1, 9, 0, 0))
                   .ending(datetime.datetime(2010, 7, 1, 14, 0, 0))
                   .within(event_folder))

            browser.login()
            browser.visit(page)
            self.assertEqual(
                ['Event which ended a few hours ago', 'Today event', 'Future event'],
                self._get_event_titles_from_block(browser)
            )

    @browsing
    def test_contributor_can_see_inactive_events_in_event_listing_block(self, browser):
        enable_behavior('plone.app.dexterity.behaviors.metadata.IPublication', 'ftw.events.EventPage')

        page = create(Builder('sl content page').titled(u'Content Page'))
        create(Builder('event listing block')
               .within(page)
               .titled(u'Not relevant for this test'))

        event_folder = create(Builder('event folder').within(page))
        create(Builder('event page')
               .titled(u'Future Event')
               .within(event_folder)
               .having(effective=datetime.datetime.now() + datetime.timedelta(days=10)))

        # Make sure a contributor can see inactive news.
        contributor = create(Builder('user').named('A', 'Contributor').with_roles('Contributor'))
        browser.login(contributor).visit(page)
        self.assertEqual(
            ['Future Event'],
            self._get_event_titles_from_block(browser),
        )

        # Make sure an anonymous user does not see the inactive news.
        browser.logout().visit(page)
        self.assertEquals(
            [],
            self._get_event_titles_from_block(browser),
        )

    @browsing
    def test_block_without_events_can_be_marked_as_hidden(self, browser):
        """
        This test makes sure that there is a CSS class "hidden" on the block
        if the block is empty and the block has been configured accordingly.
        """
        page = create(Builder('sl content page'))
        block = create(Builder('event listing block')
                       .within(page)
                       .titled(u'Event listing block'))

        def _block_has_hidden_class(browser):
            return 'hidden' in browser.css('.ftw-events-eventlistingblock').first.attrib['class']

        browser.login()

        # Make sure the block has no "hidden" class.
        browser.visit(page)
        self.assertFalse(_block_has_hidden_class(browser))

        # Edit the block.
        browser.visit(block, view='edit')
        browser.fill({u'Hide empty block': True}).find('Save').click()

        # Make sure the block has a "hidden" class now.
        browser.visit(page)
        self.assertTrue(_block_has_hidden_class(browser))
