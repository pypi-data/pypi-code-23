import json
import re
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from threading import Thread

from pyexpress.httpconstants import HttpConstants
from pyexpress.httpnext import HttpNext
from pyexpress.httprequest import HttpRequest
from pyexpress.httpresponse import HttpResponse


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class HttpServerHelper(BaseHTTPRequestHandler):
    _uses = {}
    _gets = {}
    _deletes = {}
    _posts = {}
    _puts = {}
    _server_thread = None

    @classmethod
    def start(cls, port):
        print("Listening on port " + str(port))
        server = ThreadedHTTPServer(('', port), HttpServerHelper)
        cls._server_thread = Thread(target=server.serve_forever)
        cls._server_thread.daemon = True
        cls._server_thread.start()

    @classmethod
    def stop(cls):
        if cls._server_thread is not None:
            cls._server_thread.stop()
        else:
            raise Exception("Server not configured")

    @classmethod
    def _url_to_regex(cls, url):
        if url.endswith('/'):
            url = url[:-1]
        return "^" + re.sub("/:([^/]+)", "/(?P<\g<1>>[^/]+)", url) + "(/|)$"

    @classmethod
    def use(cls, url, callback):
        cls._uses[cls._url_to_regex(url)] = callback

    @classmethod
    def get(cls, url, callback):
        cls._gets[cls._url_to_regex(url)] = callback

    @classmethod
    def delete(cls, url, callback):
        cls._deletes[cls._url_to_regex(url)] = callback

    @classmethod
    def post(cls, url, callback):
        cls._posts[cls._url_to_regex(url)] = callback

    @classmethod
    def put(cls, url, callback):
        cls._puts[cls._url_to_regex(url)] = callback

    def do_GET(self):
        self._simple_request(HttpConstants.METHOD_GET)

    def do_DELETE(self):
        self._simple_request(HttpConstants.METHOD_DELETE)

    def do_POST(self):
        self._complex_request(HttpConstants.METHOD_POST)

    def do_PUT(self):
        self._complex_request(HttpConstants.METHOD_PUT)

    def _simple_request(self, method):
        try:
            cutted_path = self.path.split('?')
            path = cutted_path[0]
            if len(cutted_path) > 1:
                query = cutted_path[1]
            else:
                query = None

            if method == HttpConstants.METHOD_DELETE:
                listeners = self._deletes
            else:
                listeners = self._gets

            query_params = {}
            if query is not None:
                query_array = query.split('&')
                for query_elem in query_array:
                    q = query_elem.split('=')
                    if len(q) == 2:
                        query_params[q[0]] = q[1]

            http_next = HttpNext()
            for url in self._uses.keys():
                regex_result = re.match(url, path)
                if regex_result is not None:
                    path_params = {}
                    for res in regex_result.groupdict().keys():
                        path_params[res] = regex_result.group(res)

                    http_request = HttpRequest(path, method, self.headers, path_params, query_params, None)
                    http_response = HttpResponse(self)
                    http_next.append(http_request, http_response, self._uses[url])

            for url in listeners.keys():
                regex_result = re.match(url, path)
                if regex_result is not None:
                    path_params = {}
                    for res in regex_result.groupdict().keys():
                        path_params[res] = regex_result.group(res)

                    http_request = HttpRequest(path, method, self.headers, path_params, query_params, None)
                    http_response = HttpResponse(self)
                    http_next.append(http_request, http_response, listeners[url])

            if http_next.has_next():
                http_next.next()
            else:
                HttpResponse(self).status(404).send()
        except Exception as e:
            HttpResponse(self).status(500).send(str(e).encode("UTF-8"))

    def _complex_request(self, method):
        try:
            cutted_path = self.path.split('?')
            path = cutted_path[0]
            if len(cutted_path) > 1:
                query = cutted_path[1]
            else:
                query = None

            if method == HttpConstants.METHOD_PUT:
                listeners = self._puts
            else:
                listeners = self._posts

            query_params = {}
            if query is not None:
                query_array = query.split('&')
                for query_elem in query_array:
                    q = query_elem.split('=')
                    if len(q) == 2:
                        query_params[q[0]] = q[1]

            body_params = []
            if 'Content-Type' in self.headers:
                header_content_type = self.headers['Content-Type']
            else:
                header_content_type = HttpConstants.CONTENT_TYPE_JSON

            if 'Content-Length' in self.headers:
                content_len = int(self.headers.get('Content-Length'))
                if content_len > 0:
                    post_body = self.rfile.read(content_len)
                    if header_content_type == HttpConstants.CONTENT_TYPE_JSON:
                        body_params = json.loads(post_body.decode("utf-8"))
                    elif header_content_type == HttpConstants.CONTENT_TYPE_WWW_FORM:
                        body_params = {}
                        arr = post_body.decode("utf-8").split("&")
                        for param in arr:
                            param_arr = param.split("=", 1)
                            key = param_arr[0]
                            value = param_arr[1]
                            body_params[key] = value
                    else:
                        raise Exception(
                            "Content-Type must be " + HttpConstants.CONTENT_TYPE_JSON
                            + " or " + HttpConstants.CONTENT_TYPE_WWW_FORM
                        )

            http_next = HttpNext()
            for url in self._uses.keys():
                regex_result = re.match(url, path)
                if regex_result is not None:
                    path_params = {}
                    for res in regex_result.groupdict().keys():
                        path_params[res] = regex_result.group(res)

                    http_request = HttpRequest(path, method, self.headers, path_params, query_params, body_params)
                    http_response = HttpResponse(self)
                    http_next.append(http_request, http_response, self._uses[url])

            for url in listeners.keys():
                regex_result = re.match(url, path)
                if regex_result is not None:
                    path_params = {}
                    for res in regex_result.groupdict().keys():
                        path_params[res] = regex_result.group(res)

                    http_request = HttpRequest(path, method, self.headers, path_params, query_params, body_params)
                    http_response = HttpResponse(self)
                    http_next.append(http_request, http_response, listeners[url])

            if http_next.has_next():
                http_next.next()
            else:
                HttpResponse(self).status(404).send()
        except Exception as e:
            HttpResponse(self).status(500).send(str(e).encode("UTF-8"))
