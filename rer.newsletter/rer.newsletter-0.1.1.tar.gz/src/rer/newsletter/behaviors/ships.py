# -*- coding: utf-8 -*-
from zope.interface import alsoProvides
from zope.interface import Interface


class IShippable(Interface):
    """Marker interface for ships object"""


alsoProvides(IShippable)
