#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from collections import deque
from . import excepts
from .const import Spec
from .reply import Reply
from .message import Message


async def _connect_to_spec(address, *, loop=None):
    host, port = address
    message = Message()
    reader, writer = await asyncio.open_connection(host, port, loop=loop)
    conn = SpecConnection(reader, writer, message, address=address, loop=loop)
    await conn.get_name()
    return conn


async def _search_for_spec(address, *, loop=None):
    host, spec = address
    for port in range(Spec.MinPort, Spec.MaxPort):
        conn = await _connect_to_spec((host, port), loop=loop)
        if conn.name == spec:
            return conn
        else:
            conn.close()
    raise excepts.SpecConnectionError('Could not find such spec connection')


async def create_connection(address, *, loop=None):
    host, spec = address
    loop = loop or asyncio.get_event_loop()
    try:
        int(spec)
    except ValueError:
        return await _search_for_spec(address, loop=loop)
    return await _connect_to_spec(address, loop=loop)


class SpecConnection:
    def __init__(self, reader, writer, message, *, address, loop=None):
        self.name = ''
        self._reader = reader
        self._writer = writer
        self.message = message
        self._address = address
        self._loop = loop
        self._waiters = deque()
        self._reply = Reply()
        self._reader_task = asyncio.ensure_future(self._read_data(), loop=self._loop)

    async def get_name(self):
        header, name = await self.send(self.message.hello())
        self.name = name

    def __repr__(self):
        host, port = self._address
        return f'<Async SpecConnection to {self.name} running at {host}:{port}>'

    async def _read_data(self):
        while not self._reader.at_eof():
            try:
                data = await self._reader.read(Spec.MaxChunkSize)
            except asyncio.CancelledError:
                break
            self._process_answer(data)

    def _process_answer(self, data):
        for header, answer in self._reply.unpack(data):
            waiter, = self._waiters.popleft()
            waiter.set_result((header, answer))

    def send(self, message):
        if self._reader is None or self._reader.at_eof():
            raise excepts.SpecConnectionError('Spec connection was closed')
        fut = self._loop.create_future()
        self._writer.write(message)
        self._waiters.append((fut,))
        return fut

    def close(self):
        self._do_close()

    def _do_close(self):
        self._writer.transport.close()
        self._reader_task.cancel()
        self._reader_task = None
        self._writer = None
        self._reader = None
        self._waiters = None
