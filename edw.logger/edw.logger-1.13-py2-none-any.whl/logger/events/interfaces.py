from zope.interface import Interface


class IPastedObject(Interface):
    """ Marker interface for objects being pasted. Used in event subscribers.
    """