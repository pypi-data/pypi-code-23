# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.app.contentlisting.interfaces import IContentListing
from Products.Five.browser import BrowserView


class TransparencyView(BrowserView):
    def sections(self):
        context = aq_inner(self.context)
        brains = context.getFolderContents({'portal_type': 'TransparencySection'})  # noqa
        return IContentListing(brains)
