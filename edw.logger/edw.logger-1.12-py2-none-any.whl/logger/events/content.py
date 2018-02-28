from datetime import datetime

from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import zope.lifecycleevent.interfaces as zci
from zope.container.interfaces import IContainerModifiedEvent

from edw.logger.util import get_user_data

from edw.logger.events.base import BaseEvent, logger
from edw.logger.events.interfaces import IPastedObject


class ObjectEvent(BaseEvent):
    """ Base class for content events.
    """

    _action = None

    def log(self, obj, event):
        req = getattr(obj, 'REQUEST', None)
        url = getattr(obj, 'absolute_url', lambda: '')()
        action = getattr(url, 'split', lambda sep: [''])('/')[-1]
        user_data = get_user_data(req)

        return {
            "IP": user_data.get('ip'),
            "User": user_data.get('user'),
            "Date": datetime.now().isoformat(),
            "URL": url,
            "Action": action,
            "Type": self._action,
            "LoggerName": logger.name
        }


class ObjectCreatedEvent(ObjectEvent):
    _action = "Create"

    def _skip(self, obj, event):
        return zci.IObjectCopiedEvent.providedBy(event)


class ObjectMovedEvent(ObjectEvent):
    _action = "Move"

    def log(self, obj, event):
        if event.oldParent:
            # if it doesn't have a parent this is an add.
            return self.log_move(obj, event)

    def log_move(self, obj, event):
        result = super(ObjectMovedEvent, self).log(obj, event)
        result['NewPath'] = obj.absolute_url()
        result['OldPath'] = '{}/{}'.format(
            event.oldParent.absolute_url(), event.oldName)

        if event.oldParent == event.newParent:
            result['Type'] = 'Rename'

        return result

    def _skip(self, obj, event):
        return (
            zci.IObjectRemovedEvent.providedBy(event) or
            zci.IObjectAddedEvent.providedBy(event)
        )


class ObjectCopiedEvent(ObjectEvent):
    _action = "Copy"

    def log(self, obj, event):
        result = super(ObjectCopiedEvent, self).log(event.original, event)
        result['Original'] = event.original.absolute_url()
        result['CopyName'] = obj.getId()

        # mark new object with IPastedObjects so it can be correctly logged
        # by the ObjectAddedEvent handler as a 'Paste'.
        alsoProvides(obj, IPastedObject)

        return result


class ObjectModifiedEvent(ObjectEvent):
    _action = "Modify"

    def _skip(self, obj, event):
        return IContainerModifiedEvent.providedBy(event)


class ObjectAddedEvent(ObjectEvent):
    _action = "Add"

    def log(self, obj, event):
        result = super(ObjectAddedEvent, self).log(obj, event)
        if IPastedObject.providedBy(obj):
            result['Type'] = 'Paste'
            # cleanup marker interface used for logging
            noLongerProvides(obj, IPastedObject)
        return result


class ObjectRemovedEvent(ObjectEvent):
    _action = "Remove"


handler_removed = ObjectRemovedEvent()
handler_added = ObjectAddedEvent()
handler_modified = ObjectModifiedEvent()
handler_created = ObjectCreatedEvent()
handler_moved = ObjectMovedEvent()
handler_copied = ObjectCopiedEvent()
