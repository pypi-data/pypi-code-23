import yaml
import aiohttp_jinja2

from aiohttp import web
from trackerfw.route import Route
from trackerfw.module import Module

__all__ = ['Trackers']

class Trackers(Module):
    @property
    def routes(self):
        with open(self.webserver.basedir + 'config/trackers.yml', 'r') as file:
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
                    if 'file' in route:
                        handler = self.file_handler(route['file'])
                    else:
                        handler = self.cancel_handler

                    hostname, path = pattern.split('/', 1)

                    yield Route(
                        handler,
                        route,
                        hostname=hostname,
                        path='/' + path
                    )

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
