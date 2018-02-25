from crawlster.helpers.extract import Content


class HttpResponse(object):
    """Class representing a http response"""

    def __init__(self, request, status_code, headers, body):
        """Initializes the http response object

        Args:
            request (HttpRequest):
                The request that produces this response
            status_code (int):
                The status code as a number
            headers (dict):
                The response headers
            body (bytes or None):
                The body of the response, if any
        """
        self.request = request
        self.status_code = status_code
        self.headers = headers
        if isinstance(body, str):
            body = body.encode()
        if not isinstance(body, bytes):
            raise TypeError(
                'body must be in bytes, not {}'.format(type(body).__name__))
        self.body = body

    @property
    def body_str(self):
        """Returns the decoded content of the request, if possible.

        May raise UnicodeDecodeError if the body does not represent a valid
        unicode encoded sequence.
        """
        return self.body.decode()

    @property
    def body_bytes(self):
        return self.body

    @property
    def server(self):
        """Returns the server header if available"""
        return self.headers.get('Server')

    @property
    def content_type(self):
        """Returns the response content type if available"""
        return self.headers.get('Content-Type')

    def is_success(self):
        return self.status_code < 400

    @property
    def extract(self):
        return Content(self.body_str)
