# -*- coding: utf-8 -*

from tornado.web import RequestHandler as TornadoRequestHandler
from kwikapi import BaseRequest, BaseResponse, BaseRequestHandler

class TornadoRequest(BaseRequest):

    def __init__(self, req_hdlr):
        super().__init__()
        self._request = req_hdlr.request
        self.response = TornadoResponse(req_hdlr)

    @property
    def url(self):
        return self._request.uri

    @property
    def method(self):
        return self._request.method

    @property
    def body(self):
        return self._request.body

    @property
    def headers(self):
        return self._request.headers

class TornadoResponse(BaseResponse):
    def __init__(self, req_hdlr):
        super().__init__()
        self._req_hdlr = req_hdlr
        self.headers = {}

    def write(self, data, proto, stream=False):
        super().write(data, proto, stream=stream)

        for k, v in self.headers.items():
            self._req_hdlr.set_header(k, v)

        d = self._data

        if not stream:
            self._req_hdlr.write(d)
            return

        for x in d:
            self._req_hdlr.write(x)

    def flush(self):
        self._req_hdlr.flush()

    def close(self):
        self._req_hdlr.finish()

class RequestHandler(TornadoRequestHandler):
    def __init__(self, *args, **kwargs):
        api = kwargs.pop('api')
        default_version = kwargs.pop('default_version', None)
        self.kwik_req_hdlr = BaseRequestHandler(api, default_version)

        super().__init__(*args, **kwargs)

    def _handle(self):
        self.kwik_req_hdlr.handle_request(TornadoRequest(self))

    get = post = _handle
