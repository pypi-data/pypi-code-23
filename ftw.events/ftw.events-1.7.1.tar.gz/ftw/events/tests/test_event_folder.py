from ftw.builder import Builder
from ftw.builder import create
from ftw.events.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from Products.CMFPlone.interfaces.syndication import IFeedSettings
import transaction


class TestEventFolder(FunctionalTestCase):

    @browsing
    def test_create_event_folder(self, browser):
        self.grant('Manager')
        browser.login().open()
        factoriesmenu.add('Event Folder')

        browser.fill({'Title': 'Activities'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals('http://nohost/plone/activities/view', browser.url)

    @browsing
    def test_event_folder_has_empty_listing_block(self, browser):
        self.grant('Manager')
        folder = create(Builder('event folder'))
        browser.login().visit(folder, view='@@simplelayout-view')
        self.assertEqual(
            ['No content available.'],
            browser.css('.sl-layout .ftw-events-eventlistingblock').text
        )

    @browsing
    def test_event_folder_rss_feed_only_renders_event_pages(self, browser):
        self.grant('Manager')
        folder = create(Builder('event folder'))
        event1 = create(Builder('event page').titled(u'Event 1').within(folder))
        event2 = create(Builder('event page').titled(u'Event 2').within(folder))

        IFeedSettings(folder).enabled = True
        transaction.commit()

        # Make sure the event folder contains the event listing block
        # and two event pages.
        self.assertEqual(
            ['ftw.events.EventListingBlock', 'ftw.events.EventPage', 'ftw.events.EventPage'],
            [obj.portal_type for obj in folder.listFolderContents()]
        )

        # Make sure that the RSS feed only renders the event pages,
        # not the event listing block.
        browser.login().visit(folder, view='rss.xml')
        self.assertEqual(
            [event1.Title(), event2.Title()],
            browser.css('item title').text
        )

    @browsing
    def test_event_folder_contains_links_to_rss_feeds_of_block(self, browser):
        """
        This test makes sure that the feed links of the event listing block
        (which is created automatically after the creation of the event folder)
         are rendered in the source of the event folder.
        """
        self.grant('Manager')
        folder = create(Builder('event folder'))
        browser.login()

        browser.visit(folder)
        self.assertEqual(
            [
                (
                    'application/rss+xml',
                    'http://nohost/plone/ftw-events-eventfolder/events/RSS',
                    'Events - RSS 1.0'
                ),
                (
                    'application/rss+xml',
                    'http://nohost/plone/ftw-events-eventfolder/events/rss.xml',
                    'Events - RSS 2.0'
                ),
                (
                    'application/rss+xml',
                    'http://nohost/plone/ftw-events-eventfolder/events/atom.xml',
                    'Events - Atom'
                )
            ],
            [
                (link.attrib['type'], link.attrib['href'], link.attrib['title'])
                for link in browser.css('link[rel="alternate"]')
            ]
        )

        # Disable syndication on the event listing block and make sure
        # the feed links are no longer rendered in the source of the
        # event folder.
        # Note that a default event listing block is created
        # automatically in the event folder.
        block = folder.listFolderContents(
            contentFilter={'portal_type': 'ftw.events.EventListingBlock'}
        )[0]
        IFeedSettings(block).enabled = False
        transaction.commit()

        browser.visit(folder)
        self.assertEqual([], browser.css('link[rel="alternate"]'))

    @browsing
    def test_event_folder_contains_links_to_rss_feeds_of_multiple_blocks(self, browser):
        """
        This test makes sure that the feed links of multiples event listing blocks
        are rendered in the source of the event folder.
        """
        self.grant('Manager')
        folder = create(Builder('event folder'))
        create(Builder('event listing block')
               .titled(u'Event Listing Block 2')
               .within(folder))
        browser.login()

        browser.visit(folder)
        self.assertEqual(
            [
                (
                    'application/rss+xml',
                    'http://nohost/plone/ftw-events-eventfolder/events/RSS',
                    'Events - RSS 1.0'
                ),
                (
                    'application/rss+xml',
                    'http://nohost/plone/ftw-events-eventfolder/events/rss.xml',
                    'Events - RSS 2.0'
                ),
                (
                    'application/rss+xml',
                    'http://nohost/plone/ftw-events-eventfolder/events/atom.xml',
                    'Events - Atom'
                ),
                (
                    'application/rss+xml',
                    'http://nohost/plone/ftw-events-eventfolder/event-listing-block-2/RSS',
                    'Event Listing Block 2 - RSS 1.0'
                ),
                (
                    'application/rss+xml',
                    'http://nohost/plone/ftw-events-eventfolder/event-listing-block-2/rss.xml',
                    'Event Listing Block 2 - RSS 2.0'
                ),
                (
                    'application/rss+xml',
                    'http://nohost/plone/ftw-events-eventfolder/event-listing-block-2/atom.xml',
                    'Event Listing Block 2 - Atom'
                )
            ],
            [
                (link.attrib['type'], link.attrib['href'], link.attrib['title'])
                for link in browser.css('link[rel="alternate"]')
            ]
        )
