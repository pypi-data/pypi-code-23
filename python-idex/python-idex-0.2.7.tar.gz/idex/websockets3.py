import asyncio
import json
import sys
import threading

from websockets import connect


class IdexWebsocket:

    WSS_URL = 'wss://api.idex.market'

    def __init__(self, market):
        self._market = market

    def __await__(self):
        return self._async_init().__await__()

    async def _async_init(self):
        self._conn = connect(self.WSS_URL)
        self.websocket = await self._conn.__aenter__()

        await self.websocket.send(json.dumps({"subscribe": self._market}))
        return self

    async def close(self):
        await self.websocket.send(json.dumps({"unsubscribe": self._market}))
        await self._conn.__aexit__(*sys.exc_info())

    async def recv(self):
        return await self.websocket.recv()


class IdexWebsocket2(threading.Thread):

    def __init__(self, market, consumer):
        threading.Thread.__init__(self)
        self._market = market
        self._consumer = consumer

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._run())

    async def _run(self):
        self._socket = await IdexWebsocket(self._market)
        try:
            while True:
                await self._consumer(await self._socket.recv())  # "Hello!"
        finally:
            await self._socket.close()
