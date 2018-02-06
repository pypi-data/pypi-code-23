from ftw.events.interfaces import IEventListingBlock
from plone import api
from plone.app.layout.links.viewlets import RSSViewlet
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class EventFolderRSSViewlet(RSSViewlet):
    """
    This custom RSS viewlet renders the RSS links in the head tag
    of an event folder for all its event listing blocks having
    syndication enabled.
    """
    index = ViewPageTemplateFile('templates/rsslink.pt')

    def update(self):
        super(EventFolderRSSViewlet, self).update()
        self.rsslinks = []
        for block in self.get_blocks_with_syndication_enabled():
            self.rsslinks.extend(self.getRssLinks(block))

    def get_blocks_with_syndication_enabled(self):
        blocks = api.content.find(
            context=self.context,
            object_provides=IEventListingBlock.__identifier__,
        )
        blocks = [brain.getObject() for brain in blocks]
        blocks = filter(
            lambda block: IFeedSettings(block).enabled,
            blocks
        )
        return blocks
