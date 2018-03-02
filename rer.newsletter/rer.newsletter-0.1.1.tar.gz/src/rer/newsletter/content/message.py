# -*- coding: utf-8 -*-
from plone.app.contenttypes.content import Folder
from rer.newsletter.interfaces import IMessage
from zope.interface import implementer


@implementer(IMessage)
class Message(Folder):
    pass
