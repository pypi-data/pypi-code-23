import aiohttp_jinja2

from aiohttp import web

class Module(object):
    def __init__(self, webserver):
        self.webserver = webserver

    def routes():
        raise Exception('please override `routes`')

    async def handler(request):
        pass
