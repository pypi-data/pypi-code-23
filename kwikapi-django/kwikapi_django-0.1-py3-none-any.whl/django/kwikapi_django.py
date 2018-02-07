# -*- coding: utf-8 -*

from django.http import HttpResponse
from django.http import StreamingHttpResponse

from kwikapi import BaseRequest, BaseResponse, BaseRequestHandler

class DjangoRequest(BaseRequest):
    def __init__(self, request):
        super().__init__()
        self.raw_request = self._request = request
        self.response = DjangoResponse(self._request)

    @property
    def url(self):
        return self._request.get_full_path()

    @property
    def method(self):
        return self._request.method

    @property
    def body(self):
        return self._request

    @property
    def headers(self):
        return self._request.META

class DjangoResponse(BaseResponse):
    def __init__(self, request):
        self._request = request
        self.raw_response = self._response = None
        self.headers = {}

    def write(self, data, proto, stream=False):
        super().write(data, proto, stream=stream)

        data = self._data
        r = StreamingHttpResponse(data) if stream else HttpResponse(data)

        for k, v in self.headers.items():
            r[k] = v

        # TODO: why this?
        self.headers = r

        self.raw_response = self._response = r

    def flush(self):
        self._response.flush()

    def close(self):
        # Django response doesn't support a close method
        # so we do nothing here.
        pass

class RequestHandler(BaseRequestHandler):
    def handle_request(self, request):
        return super().handle_request(DjangoRequest(request))
