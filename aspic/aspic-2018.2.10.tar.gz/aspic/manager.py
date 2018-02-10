#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from .connection import create_connection
from .qonnection import Qonnection


class __Manager:
    """
    This object must never be used directly, because it is a singleton object.
    Usually, you do not need to make a connection yourself, but in case you do,
    you should use it like this:
    
    from aspic import manager
    connection = manager.qonnect((host, port))
    
    """
    def __init__(self):
        self._connections = {}

    async def connect(self, address, *, loop=None):
        """Use this method if your application uses asyncio event loop"""
        self._loop = loop or asyncio.get_event_loop()
        if address not in self._connections:
            self._connections[address] = await create_connection(address, loop=self._loop)
        return self._connections[address]

    def qonnect(self, address):
        """Use this method if your application uses Qt event loop"""
        if address not in self._connections:
            self._connections[address] = Qonnection(address)
        return self._connections[address]

    def disconnect(self, address):
        if address in self._connections:
            self._connections[address].close()
            del self._connections[address]

    def abort(self):
        for address in self._connections:
            self._connections[address].abort()


manager = __Manager()
