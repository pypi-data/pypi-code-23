# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from rer.newsletter.content.channel import Channel


class MessagePreview(BrowserView):
    """ view for message preview """

    def getMessageStyle(self):
        for obj in self.context.aq_chain:
            if isinstance(obj, Channel):
                return obj.css_style

    def getMessagePreview(self):
        channel = None
        for obj in self.context.aq_chain:
            if isinstance(obj, Channel):
                channel = obj
                break
        if channel:
            body = ''
            body = channel.header.output if channel.header else u''
            body += self.context.text.output if self.context.text else u''
            body += channel.footer.output if channel.footer else u''

        return body
