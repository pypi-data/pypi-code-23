#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from .manager import manager


class Motor:
    @classmethod
    async def create(cls, address, name, update=None, *, loop=None):
        motor = cls()
        await motor._connect(address, name, update, loop=loop)
        return motor

    async def _connect(self, address, name, update, *, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._address = address
        self._name = name
        self._manager = manager
        self._update = update
        self._position = 0
        self._connection = await self._manager.connect(self._address, loop=self._loop)
        self._message = self._connection.message
        await self._connection.send(self._message.motor_register_position(self._name))
        self.update()

    def update(self):
        if callable(self._update):
            self._update(self._name, self._position)

    async def get_position(self):
        _, self._position = await self._connection.send(self._message.motor_read_position(self._name))
        self.update()
        return self._position

    def __del__(self):
        self._connection.close()
        self._connection = None
        self._message = None
