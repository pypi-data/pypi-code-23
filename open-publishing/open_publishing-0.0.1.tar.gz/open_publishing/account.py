from .object_events import ObjectEvents
from .core import DatabaseObject

class Account(DatabaseObject):
    _object_class = 'account'

    def __init__(self,
                 context,
                 account_id):
        super(Account, self).__init__(context,
                                   account_id)
        self._events = ObjectEvents(self)

    @property
    def events(self):
        return self._events

    @property
    def account_id(self):
        return self._object_id

    def _on_changed(self):
        self._context.accounts._add_to_changed(self)

    def _on_flush(self):
        self._context.accounts._remove_from_changed(self)
        
