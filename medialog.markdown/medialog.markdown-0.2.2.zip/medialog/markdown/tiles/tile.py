# -*- coding: utf-8 -*-

from plone import api

from plone.memoize.view import memoize
from plone.supermodel import model
from zope import schema
from plone.directives import form
from zope.i18nmessageid import MessageFactory
from plone.tiles import Tile
#from plone.tiles.interfaces import ITileType
#from zope.interface import provider
#from collective import dexteritytextindexer
from zope.schema import getFields


from medialog.markdown.interfaces import IMarkdownSettings
from medialog.markdown.widgets.widget import MarkdownFieldWidget
_ = MessageFactory('medialog.markdownn')


#ITile.implementedBy(MarkdownTile)

class IMarkdownTile(model.Schema):

    #dexteritytextindexer.searchable('bodytext')

    bodytext = schema.Text(
    	title=u"Body text",
    )

    form.widget(
          bodytext=MarkdownFieldWidget,
    )


class MarkdownTile(Tile):
    """A tile that displays markdown text"""

    #not sure if this is needed
    def __init__(self, context, request):
        super(MarkdownTile, self).__init__(context, request)

    def render_markdown(self):
        """Return the preview as a stringified HTML document."""
        value = self.data['bodytext']
        portal_transforms = api.portal.get_tool(name='portal_transforms')
        html = portal_transforms.convertTo('text/html', value, mimetype='text/x-web-markdown')
        return html.getData()
