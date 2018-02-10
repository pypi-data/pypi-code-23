import os
import ssl
import jinja2
import aiohttp_jinja2

from aiohttp import web
from trackerfw.handlers.dispatcher import Dispatcher
from trackerfw.handlers.subscribe import Subscribe
from trackerfw.handlers.click_tracker import ClickTracker
from trackerfw.handlers.bitly import BitLy

class Webserver(object):
    def __init__(self):
        self.app = None
        self.handlers = {}
        self._ssl_context = None
        self.basedir = os.path.dirname(os.path.realpath(__file__)) + '/'

    @property
    def ssl_context(self):
        if self._ssl_context == None:
            self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            self._ssl_context.load_cert_chain(
                self.basedir + 'certs/cert.pem',
                self.basedir + 'certs/key.pem'
            )

        return self._ssl_context

    async def shutdown(self, app):
        for _, handler in self.handlers.items():
            await handler.shutdown()

    def listen(self, host, port):
        self.app = web.Application(
            middlewares=[]
        )

        self.handlers = {
            'bit-ly': BitLy(self),
            'click-tracker': ClickTracker(self),
            'subscribe': Subscribe(self),
            'dispatcher': Dispatcher(self)
        }

        self.app.router.add_get('/$subscribe', self.handlers['subscribe'].dispatch)
        self.app.router.add_route('*', '/$route', self.handlers['dispatcher'].dispatch)
        self.app.on_shutdown.append(self.shutdown)

        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.PackageLoader('trackerfw', 'templates')
        )

        for _, handler in self.handlers.items():
            handler.setup()

        web.run_app(
            self.app,
            port=port,
            host=host,
            ssl_context=self.ssl_context
        )
