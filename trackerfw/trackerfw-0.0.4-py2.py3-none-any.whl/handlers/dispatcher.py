import os
import yaml
import aiohttp_jinja2

from aiohttp import web
from urllib.parse import unquote, urlparse
from trackerfw.handler import Handler
from trackerfw.route import Route

class Dispatcher(Handler):
    def __init__(self, server):
        self.server = server
        self.config_location = self.get_config_location()
        self.routes = None

    def parse_routes(self):
        with open(self.config_location, 'r') as file:
            config = yaml.load(file.read())

            for route in config['routes']:
                routes = []

                if 'routes' in route:
                    routes = route['routes']
                elif 'route' in route:
                    routes = [route['route']]
                else:
                    continue

                for pattern in routes:
                    if 'handler' in route:
                        handler = self.server.handlers[route['handler']].dispatch
                    elif 'file' in route:
                        handler = self.file_handler(route['file'])
                    else:
                        handler = self.cancel_handler

                    yield Route(pattern, handler, {
                        'name': route['name'],
                        'categories': route['categories']
                    })

    def get_config_location(self):
        locations = [
            os.environ['HOME'] + '/.trackers.yml',
            self.server.basedir + 'config/trackers.yml'
        ]

        for location in locations:
            if os.path.exists(location):
                return location

        raise Exception('Tracker list wasn\'t found')

    async def shutdown(self):
        pass

    def setup(self):
        self.routes = [r for r in self.parse_routes()]

    def get_cors_headers(self, request):
        headers = {
            'Access-Control-Allow-Origin': '*', # @TODO: Fix 'target' hostname, => request.scheme + '://' + request.host,
            'Access-Control-Allow-Credentials': 'true'
        }

        if 'Access-Control-Request-Headers' in request.headers:
            headers['Access-Control-Allow-Headers'] = request.headers['Access-Control-Request-Headers']

        return headers

    async def cancel_handler(self, request):
        if request.method == 'OPTIONS':
            return web.Response(
                status=200,
                headers=self.get_cors_headers(request)
            )

        return web.HTTPBadRequest(
            headers=self.get_cors_headers(request)
        )

    def file_handler(self, filename):
        content_type = 'text/plain'

        if '.js' in filename:
            content_type = 'text/javascript'
        elif '.json' in filename:
            content_type = 'application/json'

        async def handler(request):
            return web.Response(
                text=aiohttp_jinja2.render_string(filename, request, {}),
                content_type=content_type,
                headers=self.get_cors_headers(request)
            )

        return handler

    async def dispatch(self, request):
        uri = unquote(request.query['uri'])
        session_id = request.query['session_id']
        match_url = uri.split('?')[0]

        for route in self.routes:
            if route.matches(match_url):
                print('> dispatch: ' + match_url)

                parsed_uri = urlparse(uri)
                hostname = parsed_uri.netloc.split(':')[0]
                headers = request.headers
                headers['Host'] = hostname

                await self.server.handlers['subscribe'].send_websockets(
                    'trackerFound',
                    {
                        **{
                            'uri': uri,
                            'session_id': session_id
                        },
                        **route.details
                    }
                )

                return await route.handler(request.clone(
                    rel_url=uri,
                    scheme=parsed_uri.scheme,
                    method=request.method,
                    headers=headers,
                    host=hostname
                ))

        return web.HTTPNotFound()
