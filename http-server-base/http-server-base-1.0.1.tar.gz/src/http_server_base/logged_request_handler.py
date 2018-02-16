import json
import random
import string
import warnings
from typing import Union, Callable

import tornado.httpclient
from tornado import httputil
from tornado.web import RequestHandler, asynchronous, MissingArgumentError
from logging import getLogger

from http_server_base import BasicResponder

class Logged_RequestHandler(RequestHandler):
    """
    Logged_RequestHandler class
    This is a template to the handler classes.
    """
    
    # Must override
    logger_name:str
    
    # Should not override
    logger = None
    requ_id = None
    request: httputil.HTTPServerRequest
    responder_class: BasicResponder
    
    _ARG_DEFAULT = object()
    def get_body_or_query_argument(self, name, default=_ARG_DEFAULT, strip=True):
        all_args = self.request.body_arguments.copy()
        all_args.update(self.request.query_arguments)
        return self._get_argument(name=name, default=default, source=all_args, strip=strip)
    
    def get_body_or_query_arguments(self, name, strip=True):
        all_args = self.request.body_arguments.copy()
        all_args.update(self.request.query_arguments)
        return self._get_arguments(name=name, source=all_args, strip=strip)

    def initialize(self, **kwargs):
        """
        Initializes the Logged_RequestHandler
        
        Initializes the logging.
        Logs the incoming request to the DEBUG level.
        Sets an request id.
        
        Will raise an AssertionError if logger_name is not set.
        """
        assert hasattr(self, 'logger_name'), "'logger_name' must be specified for any Logged_RequestHandler child"
        
        super().initialize(**kwargs)

        self.logger = getLogger(self.logger_name)

        request_obj = self.request
        self.requ_id = self.get_query_argument('requuid', default="{0:x}".format(random.randint(0, 0xffffff)))

        self.logger.debug(f"req({self.requ_id}): Incomming HTTP: {request_obj.method} {request_obj.uri}")
        self.logger.debug(f"req({self.requ_id}): Headers: {json.dumps(dict(request_obj.headers))}")
        self.logger.debug(f"req({self.requ_id}): Querry args: {request_obj.query_arguments}")
        self.logger.debug(f"req({self.requ_id}): Body args: {request_obj.body_arguments}")

    def set_default_headers(self):
        del self._headers["Content-Type"]

    def resp_error(self, code=500, message=None):
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            self.send_error(code, reason=message)
            return
        
        responder.resp_error(self, code, message)

    def resp(self, code=200, message=None):
        BasicResponder.resp_success(handler=self, code=code, message=message)
        
    def resp_success(self, code=200, message=None, result=None):
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            self.set_status(code, message)
            return
        
        responder.resp_success(self, code, message, result)


    def generate_proxy_request(self, handler):
        """
        Generate the new instance of the tornado.httpclient.HTTPRequest.
        :param handler:
        :return:
        """
        warnings.warn("The 'generate_proxy_request' method has redundant arguments, "
            "use 'generate_proxy_HTTPRequest' instead. It is going to be changed in v1.0", DeprecationWarning, 2)
        Logged_RequestHandler.generate_proxy_HTTPRequest(self)
        
    def generate_proxy_HTTPRequest(self:'Logged_RequestHandler', server=None, uri=None) -> tornado.httpclient.HTTPRequest:
        from tornado.httpclient import HTTPRequest
        request_obj:httputil.HTTPServerRequest = self.request
        
        if (server is None):
            server = f"{request_obj.protocol}://{request_obj.host}"
        if (uri is None):
            uri = request_obj.uri
        new_url = server + uri
        
        _method = request_obj.method.upper()
        _body = None
        if (_method == 'GET'):
            pass
        elif (_method == 'DELETE'):
            pass
        else:
            _body = request_obj.body

        self.logger.info(f"proxy({self.requ_id}): Redirecting to url: {new_url}")
    
        _proxy_request = HTTPRequest(url=new_url, method=_method, body=_body, headers=request_obj.headers)
        return _proxy_request
    
    @asynchronous
    def proxy_request_async(self, *, generate_request_func: Union[None, Callable[['Logged_RequestHandler'], tornado.httpclient.HTTPRequest]]=None, **kwargs):
        """
        Proxies current request.
        """
        
        from tornado.httpclient import AsyncHTTPClient
        if (generate_request_func is None):
            generate_request_func = type(self).generate_proxy_HTTPRequest
        
        _client = AsyncHTTPClient()
        _proxy_request = generate_request_func(self, **kwargs)
        
        self.logger.debug(f"proxy({self.requ_id}): Proxy request url: {_proxy_request.method} {_proxy_request.url}")
        self.logger.debug(f"proxy({self.requ_id}): Proxy request headers: {json.dumps(dict(_proxy_request.headers))}")
        self.logger.debug(f"proxy({self.requ_id}): Proxy request body args: {_proxy_request.body}")
        self.logger.debug(f"proxy({self.requ_id}): Fetching proxy request")
        _client.fetch(_proxy_request, self.__proxied)
        return
    
    def __proxied(self, response):
        _code = response.code
        if (_code == 599):
            self.logger.error(f"resp({self.requ_id}): Internal error during proxying request. Changing request code from {_code} to 500")
            self.logger.error(f"resp({self.requ_id}): {type(response.error).__name__}: {response.error}")
            self.send_error(500, reason="Internal server error during proxying request")
            return

        self.logger.debug(f"resp({self.requ_id}): Return {_code}")
        self.set_status(_code)
        if ('content-type' in response.headers):
            self.add_header('Content-Type', response.headers['content-type'])
        elif ('content-type' in self.request.headers):
            self.add_header('Content-Type', self.request.headers['content-type'])
        if (response.body):
            self.logger.debug(f"resp({self.requ_id}): Content {response.body[:500]}")
            self.write(response.body)
        else:
            self.write(b'')
        self.finish()
        return

    # Overriding original finish to exclude 204/304 no body verification
    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        if self._finished:
            raise RuntimeError("finish() called twice")

        if chunk is not None:
            self.write(chunk)

        # Automatically support ETags and add the Content-Length header if
        # we have not flushed any content yet.
        if not self._headers_written:
            if (self._status_code == 200 and
                self.request.method in ("GET", "HEAD") and
                    "Etag" not in self._headers):
                self.set_etag_header()
                if self.check_etag_header():
                    self._write_buffer = []
                    self.set_status(304)
            # if self._status_code in (204, 304):
            #     assert not self._write_buffer, "Cannot send body with %s" % self._status_code
            #     self._clear_headers_for_304()
            elif "Content-Length" not in self._headers:
                content_length = sum(len(part) for part in self._write_buffer)
                self.set_header("Content-Length", content_length)

        if hasattr(self.request, "connection"):
            # Now that the request is finished, clear the callback we
            # set on the HTTPConnection (which would otherwise prevent the
            # garbage collection of the RequestHandler when there
            # are keepalive connections)
            self.request.connection.set_close_callback(None)

        self.flush(include_footers=True)
        self.request.finish()
        self._log()
        self._finished = True
        self.on_finish()
        self._break_cycles()

    @classmethod
    def generate_random_string(cls, N):
        return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=N))
