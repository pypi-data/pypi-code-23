# -*- coding: utf-8 -*-
from plone.app.contenttypes.content import Folder
from rer.newsletter.interfaces import IChannel
from zope.interface import implementer


@implementer(IChannel)
class Channel(Folder):
    pass
