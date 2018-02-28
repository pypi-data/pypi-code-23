import random
from inspect import isawaitable
from urllib.parse import urljoin

import aiohttp
from sanic.request import Request
from sanic.response import HTTPResponse, StreamingHTTPResponse

from brama.plugins import RouteHandlerPlugin
from .request import ProxyRequest, LocalRequest


class BaseHandler(object):
    request_class = None
    is_stream = False  # for Sanic, allows to use request.stream

    def __init__(self, route, prefix_path=None):
        self.route = route
        self.prefix_path = prefix_path
        self.is_stream = self.route.stream

    async def __call__(self, request: Request, *view_args, **view_kwargs):
        return await self._process_request(request, view_args, view_kwargs)

    async def _process_request(self, request: Request, view_args, view_kwargs):
        api_request = self.api_request_factory(request, view_args, view_kwargs)
        response = await self.run_request_middlewares(api_request)
        if response is None:
            response = await self.get_response(api_request)

        _response = await self.run_response_middlewares(api_request, response)
        return _response if _response is not None else response

    def api_request_factory(self, request: Request, view_args, view_kwargs):
        return self.request_class(self.route, request,
                                  prefix_path=self.prefix_path,
                                  view_args=view_args,
                                  view_kwargs=view_kwargs)

    async def run_request_middlewares(self, api_request):
        for plugin in api_request.enabled_plugins(
                required_methods=['process_request']):
            resp = plugin.process_request(api_request)
            if isawaitable(resp):
                resp = await resp

            if resp:
                return resp
        return None

    async def run_response_middlewares(self, api_request, response):
        for plugin in api_request.enabled_plugins(
                required_methods=['process_response']):
            resp = plugin.process_response(api_request, response)
            if isawaitable(resp):
                resp = await resp

            if resp:
                return resp
        return None

    async def get_response(self, api_request):
        raise NotImplementedError()


class ProxyHandler(BaseHandler):
    request_class = ProxyRequest

    async def _proxy_normal_response(self, api_request, url):
        async with aiohttp.ClientSession(auto_decompress=False) as sess:
            async with sess.request(api_request.method, url,
                                    data=api_request.proxy_data,
                                    headers=api_request.headers) as r:
                return HTTPResponse(body_bytes=await r.content.read(),
                                    status=r.status,
                                    headers=dict(r.headers))

    async def _proxy_stream_response(self, api_request, url):
        # TODO: Refactor to make sure session always closed.
        # and maybe add keep-alive support with upstreams

        client_session = aiohttp.ClientSession(auto_decompress=False)
        req = client_session.request(api_request.method, url,
                                     data=api_request.proxy_data,
                                     headers=api_request.headers)
        resp = await req._coro

        async def streaming_fn(response):
            try:
                async for data in resp.content.iter_any():
                    response.write(data)
            finally:
                # TODO: Websockets needs `resp.close()`
                await resp.release()
                await client_session.close()

        return StreamingHTTPResponse(streaming_fn,
                                     status=resp.status,
                                     headers=dict(resp.headers))

    def get_upstream_url(self, api_request):
        targets = self.route.upstreams.get('targets', [])
        strategy = self.route.upstreams.get('balancing', 'random')

        if strategy == 'roundrobin':
            raise NotImplementedError()
        elif strategy == 'random':
            upstream = random.choice(targets)
        else:
            raise NotImplementedError()

        # Fill upstream url 'variables' with parsed route's values.
        # `url_vars` can be extended with another helpful params, like
        # request_id, user_id, api_version, etc.
        url_vars = dict(api_request.view_kwargs)
        upstream = upstream.format(**url_vars)

        url = urljoin(upstream, api_request.path.lstrip('/'))
        url += api_request.query_string
        return url

    async def get_response(self, api_request):
        url = self.get_upstream_url(api_request)
        try:
            if api_request.route.stream:
                response = await self._proxy_stream_response(api_request, url)
            else:
                response = await self._proxy_normal_response(api_request, url)
        except aiohttp.client_exceptions.ClientConnectorError:
            # TODO
            response = HTTPResponse('Bad Gateway', status=502)
        return response


class LocalHandler(BaseHandler):
    request_class = LocalRequest

    def _get_request_handler(self, api_request):
        '''
        Returns view object basing on specified route's handler.
        :return: function
        '''
        if isinstance(self.route.handler, str):
            plugin = api_request.app.plugins_registry.get(self.route.handler,
                                                          'route_handler')
            if not plugin:
                raise ValueError('Handler {} could not be found'.format(
                    self.route.handler))
            handler_func = plugin.wrapped_object
        elif isinstance(self.route.handler, RouteHandlerPlugin):
            handler_func = self.route.handler.wrapped_object
        else:
            handler_func = self.route.handler
        return handler_func

    async def get_response(self, api_request):
        # TODO: add support for classview in future
        func = self._get_request_handler(api_request)
        result = func(api_request._original_request,
                      *api_request.view_args,
                      **api_request.view_kwargs)

        if isawaitable(result):
            result = await result

        if isinstance(result, HTTPResponse):
            return result

        status = 200
        if isinstance(result, tuple):
            data, status = result
        else:
            data = result

        return HTTPResponse(data, status=status)
