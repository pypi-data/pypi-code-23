import os
import ssl
import jinja2
import importlib.util
import aiohttp_jinja2

from aiohttp import web
from urllib.parse import unquote, urlparse
from threading import Lock
from trackerfw.router import Router

class Webserver(object):
    def __init__(self):
        self.app = None
        self._modules = None
        self._websockets = []
        self._ws_lock = Lock()
        self.router = Router()
        self._ssl_context = None
        self.basedir = os.path.dirname(os.path.realpath(__file__)) + '/'

    @property
    def websockets(self):
        with self._ws_lock:
            return [ws for ws in self._websockets]

    async def close_websockets(self, app):
        sockets = self.websockets

        for sock in sockets:
            try:
                await sock.close()
            except: pass

    async def send_websockets(self, event, data):
        sockets = self.websockets

        for sock in sockets:
            await sock.send_json({
                'type': event,
                'data': data
            })

    def _load_modules(self, name):
        spec = importlib.util.spec_from_file_location(
            name,
            self.basedir + '/modules/' + name + '.py'
        )
        py_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(py_module)

        for key in py_module.__all__:
            yield getattr(py_module, key)(self)

    @property
    def ssl_context(self):
        if self._ssl_context == None:
            self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            self._ssl_context.load_cert_chain(
                self.basedir + 'certs/cert.pem',
                self.basedir + 'certs/key.pem'
            )

        return self._ssl_context

    @property
    def modules(self):
        if self._modules == None:
            self._modules = []

            for file in os.listdir(self.basedir + '/modules/'):
                if '__' in file:
                    continue

                self._modules += [m for m in self._load_modules(file[:-3])]

        return self._modules

    async def send_patterns(self, ws):
        await ws.send_json({
            'type': 'patternList',
            'data': [
                pattern for pattern in [
                    route.pattern for route in self.router.routes
                ] if pattern != None
            ]
        })

    @web.middleware
    async def send_tracker(self, request, handler):
        response = await handler(request)
        details = request.match_info.get_info()

        if details != None and 'X-Session-Id' in request.headers:
            details['session_id'] = request.headers['X-Session-Id']

            await self.send_websockets('trackerFound', details)

        return response

    @web.middleware
    async def subscribe(self, request, handler):
        if request.path != '/$subscribe':
            return await handler(request)

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

    @web.middleware
    async def reroute(self, request, handler):
        if request.path == '/$route':
            raw_uri = unquote(request.query['uri'])
            uri = urlparse(raw_uri)
            hostname = uri.netloc.split(':')[0]
            headers = request.headers

            if 'session_id' in request.query:
                headers['X-Session-Id'] = request.query['session_id']

            headers['Host'] = hostname

            return await self.app._handle(request.clone(
                rel_url=raw_uri,
                scheme=uri.scheme,
                method=request.method,
                headers=headers,
                host=hostname
            ))

        return await handler(request)

    def listen(self, host, port):
        for module in self.modules:
            for route in module.routes:
                self.router.routes.append(route)

        self.app = web.Application(
            router=self.router,
            middlewares=[
                self.reroute,
                self.send_tracker,
                self.subscribe
            ]
        )

        self.app.on_shutdown.append(self.close_websockets)

        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.PackageLoader('trackerfw', 'templates')
        )

        web.run_app(
            self.app,
            port=port,
            host=host,
            ssl_context=self.ssl_context
        )
