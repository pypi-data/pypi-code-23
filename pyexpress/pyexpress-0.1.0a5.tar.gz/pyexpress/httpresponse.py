from pyexpress.httpresponseclosederror import HttpResponseClosedError


class HttpResponse:
    is_closed = True
    status_code = 500

    def __init__(self, http_request_handler):
        self.http_request_handler = http_request_handler
        self.is_closed = False

    def status(self, status_code):
        if self.is_closed:
            raise HttpResponseClosedError()
        self.status_code = status_code
        return self

    def send(self, data=None):
        if self.is_closed:
            raise HttpResponseClosedError()
        self.is_closed = True
        self.http_request_handler.send_response(self.status_code)
        self.http_request_handler.end_headers()
        if data is not None:
            self.http_request_handler.wfile.write(data)
