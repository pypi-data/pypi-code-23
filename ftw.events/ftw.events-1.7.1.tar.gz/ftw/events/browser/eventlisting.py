from ftw.events import _
from ftw.events.interfaces import IEventListingView
from plone import api
from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.i18n import translate
from zope.interface import implements


class EventListing(BrowserView):
    """
    This browser view renders a list of event pages based on the parameters
    defined on the event listing block which renders a link to this browser
    view.
    """
    implements(IEventListingView)

    def __init__(self, context, request):
        super(EventListing, self).__init__(context, request)
        self.batch_size = 10

    @property
    def batch(self):
        b_start = self.request.form.get('b_start', 0)
        return Batch(self.get_items(), self.batch_size, b_start)

    def get_query(self):
        block_view = api.content.get_view(
            name='block_view',
            context=self.context,
            request=self.request,
        )
        start, end = block_view.get_dates_for_query()
        block_query = block_view.get_query(start, end)
        return block_query

    def get_items(self):
        """
        Returns a list of event page brains.
        """
        catalog = api.portal.get_tool(name='portal_catalog')
        return catalog(self.get_query())

    def get_event_page_dict(self, brain):
        """
        Constructs a dict containing the data of the brain of an event page.
        """
        obj = brain.getObject()

        # Copied from "plone.app.event.portlets.portlet_events.Renderer#formatted_date".
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        date_snippet = provider(obj)

        item = {
            'title': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'brain': brain,
            'date_snippet': date_snippet,
            'location': obj.location or '',
        }
        return item

    @property
    def title(self):
        """
        Returns the title defined on the event listing block or a
        fallback title.
        """
        fallback_title = translate(
            _('more_items_view_fallback_title', default=u'Events'),
            context=self.request
        )
        return self.context.more_items_view_title or fallback_title


class EventListingRss(EventListing):

    @property
    def description(self):
        return _(u'label_feed_desc',
                 default=u'${title} - Events Feed',
                 mapping={'title': self.context.Title().decode('utf-8')})

    @property
    def link(self):
        url = self.context.absolute_url() + '/' + self.__name__
        return '<link>{}</link>'.format(url)

    def get_item_link(self, url):
        return '<link>{}</link>'.format(url)
