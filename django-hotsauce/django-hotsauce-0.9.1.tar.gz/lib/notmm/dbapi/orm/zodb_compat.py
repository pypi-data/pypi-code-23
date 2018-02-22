#!/usr/bin/env python
# -*- coding: utf-8 -*-
from schevo.backends.zodb import ZodbBackend # require zodb 3.7.4
from ._databaseproxy import DatabaseProxy

__all__ = ['ClientStorageProxy', 'ZODBFileStorageProxy']

class ClientStorageProxy(DatabaseProxy):
    def __init__(self, db_name, **kwargs):
        # XXX Hack.
        if not 'db_connection_cls' in kwargs:
            kwargs['db_connection_cls'] = ZodbBackend
        super(ZODBFileStorageProxy, self).__init__(db_name, **kwargs)

ZODBFileStorageProxy = ClientStorageProxy

