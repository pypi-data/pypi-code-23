import os

from aiohttp import web
from threading import Lock
from trackerfw.handler import Handler

class Subscribe(Handler):
    def __init__(self, server):
        self.server = server
        self._websockets = []
        self._ws_lock = Lock()

    async def send_patterns(self, ws):
        await ws.send_json({
            'type': 'patternList',
            'data': [
                pattern for pattern in [
                    route.match_pattern for route in self.server.handlers['dispatcher'].routes
                ] if pattern != None
            ]
        })

    @property
    def websockets(self):
        with self._ws_lock:
            return [ws for ws in self._websockets]

    async def send_websockets(self, event, data):
        sockets = self.websockets

        for sock in sockets:
            await sock.send_json({
                'type': event,
                'data': data
            })

    async def shutdown(self):
        sockets = self.websockets

        for sock in sockets:
            try:
                await sock.close()
            except: pass

    async def dispatch(self, request):
        print('> client connected')

        ws = web.WebSocketResponse()
        
        await ws.prepare(request)
        await self.send_patterns(ws)

        with self._ws_lock:
            self._websockets.append(ws)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
            elif msg.type == aiohttp.WSMsgType.ERROR:
                await ws.close()
            
        print('> client disconnected')

        with self._ws_lock:
            self._websockets = [w for w in self._websockets if not w.closed]

        return ws