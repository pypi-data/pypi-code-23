# Copyright (c) 2018, Neil Booth
#
# All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


__all__ = ('ClientSession', 'ServerSession')


import asyncio
import logging
import ssl

from .framing import NewlineFramer
from .rpc import RPCProcessor
from .jsonrpc import JSONRPCv2


class SessionBase(asyncio.Protocol):

    def __init__(self, rpc, framer, loop, logger):
        self.loop = loop or asyncio.get_event_loop()
        self.rpc = rpc or self.default_rpc(logger)
        self.framer = framer or self.default_framer()
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.paused = False
        self.transport = None
        # FIXME: clean up
        self.rpc.send_message = self.send_message
        self.rpc.notification_handler = self.notification_handler
        self.rpc.request_handler = self.request_handler

    def data_received(self, framed_message):
        '''Called by asyncio when a message comes in.'''
        self.using_bandwidth(len(framed_message))
        for message in self.framer.messages(framed_message):
            self.rpc.message_received(message)

    def send_message(self, message):
        '''Send a message over the connection. It is framed before sending.'''
        self.send_messages((message, ))

    def send_messages(self, messages):
        '''Send messages (an iterable) over the connection.

        They are framed before sending.'''
        framed_message = self.framer.frame(messages)
        self.using_bandwidth(len(framed_message))
        self.transport.write(framed_message)

    # External API
    def default_framer(self):
        '''Return a default framer.'''
        return NewlineFramer()

    def default_rpc(self, logger):
        '''Return a default SSL context if user provides none.'''
        job_queue = JobQueue(self.loop, logger=logger)
        return RPCProcessor(JSONRPCv2, job_queue, logger=logger)

    def connection_made(self, transport):
        '''Called by asyncio when a connection is established.'''
        self.transport = transport

    def connection_lost(self, exc):
        '''Called by asyncio when the connection closes.'''
        pass

    def pause_writing(self):
        '''Called by asyncio when the send buffer is full.'''
        self.logger.info('pausing processing whilst socket drains')
        self.paused = True

    def resume_writing(self):
        '''Called by asyncio the send buffer has room.'''
        self.logger.info('resuming processing')
        self.paused = False

    # App layer
    def is_closing(self):
        '''Return True if the connection is closing.'''
        return self.transport.is_closing()

    async def close(self):
        '''Close the connection.'''
        await self.rpc.close()
        self.transport.close()

    def abort(self):
        '''Cut the connection abruptly.'''
        self.transport.abort()

    def send_request(self, method, args=None, on_done=None):
        '''Send an RPC request over the network.'''
        request = RPCRequestOut(method, args, on_done, loop=self.loop)
        self.rpc.send_request(request)
        return request

    def send_notification(self, method, args=None):
        '''Send an RPC notification over the network.'''
        request = RPCRequest(method, args, None)
        self.rpc.send_request(request)
        return request

    def all_requests(self):
        '''Returns an iterable of all requests that have not yet completed.

        If a batch requests is outstanding, it is returned and not the
        individual requests it is comprised of.
        '''
        return self.rpc.all_requests()

    def using_bandwidth(self, amount):
        '''Called as bandwidth is consumed.

        Override to implement bandwidth management.
        '''
        pass

    def notification_handler(self, method):
        '''Return the handler for the given notification.

        The handler can be synchronous or asynchronous.'''
        return None

    def request_handler(self, method):
        '''Return the handler for the given request method.

        The handler can be synchronous or asynchronous.'''
        return None


class ClientSession(SessionBase):

    def __init__(self, host=None, port=None, *, rpc=None, loop=None,
                 logger=None, **kwargs):
        super().__init__(rpc, loop, logger)
        kwargs['host'] = host
        kwargs['port'] = port
        self.kwargs = kwargs

    async def connect(self):
        protocol_factory = partial(_Protocol, self.logger)
        transport, self.protocol = await self.loop.create_connection(
            protocol_factory, **self.kwargs)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()


class ServerSession(SessionBase):

    def __init__(self, *, rpc=None, loop=None, logger=None, **kwargs):
        super().__init__(rpc, loop, logger)
        self.kwargs = kwargs
        self.server = None

    async def listen(self):
        protocol_factory = partial(_Protocol, self.logger)
        self.server = self.loop.create_server(protocol_factory, **self.kwargs)

    async def __aenter__(self):
        await self.listen()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
