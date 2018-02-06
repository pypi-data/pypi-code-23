from Products.CMFPlone.browser.syndication.adapters import FolderFeed
from plone import api
from ftw.events.interfaces import IEventPage


class EventFolderFeed(FolderFeed):

    def _brains(self):
        catalog = api.portal.get_tool('portal_catalog')
        query = {
            'object_provides': IEventPage.__identifier__,
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
            },
            'sort_on': 'start',
            'sort_order': 'ascending',
        }
        return catalog(**query)


class EventListingBlockFeed(FolderFeed):

    def _brains(self):
        catalog = api.portal.get_tool('portal_catalog')
        query = self.get_query()
        return catalog(**query)

    def get_query(self):
        block_view = api.content.get_view(
            name='block_view',
            context=self.context,
            request=self.context.REQUEST,
        )
        block_query = block_view.get_query()
        return block_query
