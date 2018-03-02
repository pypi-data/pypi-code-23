# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView


class MessageView(BrowserView):

    def getMessageText(self):
        return self.context.text.output
