from aiohttp import streamer
from sanic.request import Request


class ApiRequest(object):
    path = None
    method = None
    headers = None
    query_string = None
    parsed_args = None
    view_args = None
    view_kwargs = None

    def __init__(self, route, original_request: Request, prefix_path=None,
                 view_args=None, view_kwargs=None):
        self.route = route
        self.prefix_path = prefix_path
        self._original_request = original_request
        self.app = original_request.app
        self.path = original_request.path
        self.method = original_request.method
        self.headers = dict(original_request.headers)
        self.parsed_args = original_request.parsed_args
        self.query_string = original_request.query_string
        self.view_args = view_args or tuple()
        self.view_kwargs = view_kwargs or dict()
        self.body_stream = self._get_body_streamer()

    def enabled_plugins(self, required_methods=()):
        return self.app.enabled_plugins(
            api=self.route.api, route=self.route,
            required_methods=required_methods)

    def _get_body_streamer(self):
        @streamer
        def request_body_stream(writer):
            while True:
                chunk = yield from self._original_request.stream.get()
                yield from writer.write(chunk)
                if not chunk:
                    break

        return request_body_stream


class ProxyRequest(ApiRequest):

    def __init__(self, *args, **kwargs):
        super(ProxyRequest, self).__init__(*args, **kwargs)
        self.path = self.get_upstream_path()

    @property
    def proxy_data(self):
        if self._original_request.stream:
            return self.body_stream
        return self._original_request.body

    def get_upstream_path(self):
        upstream_path = self.path[:]

        if self.route.strip_path:
            upstream_path = '/'
        elif not self.route.strip_path:
            if self.prefix_path:
                _clean = self.path[len(self.prefix_path):].lstrip('/')
                upstream_path = '/' + _clean
        return upstream_path

    def replace_path(self, new_path):
        self.path = new_path

    def replace_header(self, name, new_value):
        self.headers[name] = new_value

    def replace_method(self, new_method):
        self.method = new_method


class LocalRequest(ApiRequest):
    pass

    # @property
    # async def json(self):
    #     if not self._original_request.body:
    #         a = self._original_request.stream.read()
    #         raise Exception(a)
    #         self._original_request.body = await self.body_stream.get()
    #     return self._original_request.json
