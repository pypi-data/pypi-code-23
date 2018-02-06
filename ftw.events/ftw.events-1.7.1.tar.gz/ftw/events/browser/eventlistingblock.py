from Acquisition._Acquisition import aq_inner, aq_parent
from ftw.events import _
from ftw.events import utils
from ftw.events.interfaces import IEventPage
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.contenttypes.behaviors import IHiddenBlock
from plone import api
from plone.app.event.base import _prepare_range, filter_and_resort
from plone.dexterity.utils import safe_utf8
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.i18n import translate
import datetime


class EventListingBlockView(BaseBlock):
    template = ViewPageTemplateFile('templates/eventlistingblock.pt')

    def get_block_info(self):
        """
        This method returns a dict containing information to be used in
        the block's template.
        """
        rss_link_url = ''
        if self.context.show_rss_link:
            rss_link_url = '/'.join([self.context.absolute_url(),
                                     'events_rss'])

        more_items_link_url = ''
        if self.context.show_more_items_link:
            more_items_link_url = '/'.join([self.context.absolute_url(), 'events'])

        more_items_link_label = (
            self.context.more_items_link_label or
            translate(_('more_items_link_label', default=u'More Items'),
                      context=self.request)
        )

        info = {
            'title': self.context.title,
            'show_title': self.context.show_title,
            'rss_link_url': rss_link_url,
            'more_items_link_url': more_items_link_url,
            'more_items_link_label': more_items_link_label,
            'hide_empty_block':  self.context.hide_empty_block,
        }

        return info

    def get_items(self):
        """
        Returns a list of dicts where each dict contains the data of an
        event page. It is called from the template.
        """
        catalog = getToolByName(self.context, 'portal_catalog')

        start, end = self.get_dates_for_query()
        brains = catalog.searchResults(
            **self.get_query(start, end)
        )

        # Inspired by `plone.app.event.base.get_events`.
        brains = filter_and_resort(
            context=self.context, brains=brains, start=start,
            end=end, sort='start', sort_reverse=False
        )

        if self.context.quantity:
            brains = brains[:self.context.quantity]

        items = [self.get_event_page_dict(brain) for brain in brains]

        return items

    def get_dates_for_query(self):
        start = None
        if self.context.exclude_past_events:
            # Start from midnight of today. This way the query will also
            # include events which have ended just a few hours ago.
            midnight_of_today = datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            start = midnight_of_today

        # Inspired by `plone.app.event.base.get_events`.
        start, end = _prepare_range(self.context, start, None)
        return start, end

    def get_query(self, start=None, end=None):
        query = {
            'object_provides': IEventPage.__identifier__,
            'sort_on': 'start',
        }

        # Inspired by `plone.app.event.base.get_events`.
        if start:
            # All events from start date ongoing:
            # The minimum end date of events is the date from which we search.
            query['end'] = {'query': start, 'range': 'min'}
        if end:
            # All events until end date:
            # The maximum start date must be the date until we search.
            query['start'] = {'query': end, 'range': 'max'}

        parent = aq_parent(aq_inner(self.context))
        if self.context.current_context:
            # `parent` is the object containing this block.
            path = '/'.join(parent.getPhysicalPath())
            query['path'] = {'query': path}

        elif self.context.filter_by_path:
            portal_path = '/'.join(api.portal.get().getPhysicalPath())
            paths = ['/'.join([portal_path, path])
                     for path in self.context.filter_by_path]
            query['path'] = {'query': paths}

        subjects = self.context.subjects
        if subjects:
            query['Subject'] = map(safe_utf8, subjects)

        # Show inactive events if the current user is allowed to add events on the
        # parent of the event listing block. We must only render the inactive events
        # if the block renders events from its parent (in order not to allow the user
        # to view news items he is not allowed to see).
        if self.context.current_context \
                and not self.context.filter_by_path \
                and api.user.has_permission('ftw.events: Add Event Page', obj=parent):
            query['show_inactive'] = True

        return query

    def get_event_page_dict(self, brain):
        """
        Constructs a dict containing the data of the brain of an event page.
        """
        obj = brain.getObject()

        description = ''
        if self.context.show_description:
            description = brain.Description
        if self.context.description_length:
            description = utils.crop_text(
                description, self.context.description_length
            )

        # Copied from "plone.app.event.portlets.portlet_events.Renderer#formatted_date".
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        date_snippet = provider(obj)

        item = {
            'title': brain.Title,
            'description': description,
            'url': brain.getURL(),
            'brain': brain,
            'date_snippet': date_snippet,
            'location': obj.location or '',
        }
        return item
