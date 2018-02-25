import requests
import requests.auth
import requests.exceptions

from crawlster.helpers.base import BaseHelper
from crawlster.helpers.http.request import (
    HttpRequest, GetRequest, PostRequest)
from crawlster.helpers.http.response import HttpResponse


class RequestsHelper(BaseHelper):
    """Helper for making HTTP requests using the requests library"""
    name = 'http'

    STAT_DOWNLOAD = 'http.download'
    STAT_UPLOAD = 'http.upload'
    STAT_REQUESTS = 'http.requests'
    STAT_HTTP_ERRORS = 'http.errors'

    def __init__(self):
        super(RequestsHelper, self).__init__()
        self.session = None

    def initialize(self):
        """Initializes the session used for making requests"""
        self.session = requests.session()

    def open(self, http_request: HttpRequest):
        """Opens a given HTTP request.

        Args:
            http_request (HttpRequest):
                The crawlster.helpers.http.request.HttpRequest instance
                with the required info for making the request

        Returns:
            crawlster.helpers.http.response.HttpResponse
        """
        self.crawler.stats.incr(self.STAT_REQUESTS)

        try:
            resp = self.session.request(
                http_request.method, http_request.url,
                http_request.query_params,
                http_request.data, http_request.headers
            )
            http_resp = HttpResponse(
                http_request, resp.status_code, resp.headers, resp.content
            )
            self.crawler.stats.incr(self.STAT_DOWNLOAD,
                                    by=self._compute_resp_size(http_resp))
            self.crawler.stats.incr(self.STAT_UPLOAD,
                                    by=self._compute_req_size(http_request))
            return http_resp
        except requests.exceptions.RequestException as e:
            self.crawler.stats.add(self.STAT_HTTP_ERRORS, e)
            self.crawler.log.error(str(e))

    def get(self, url, query_params=None, headers=None):
        """Makes a GET request"""
        return self.open(
            GetRequest(url, query_params or {}, headers or {})
        )

    def post(self, url, data=None, query_params=None, headers=None):
        """Makes a POST request"""
        return self.open(PostRequest(url, data, query_params, headers))

    def patch(self, url, data=None, query_params=None, headers=None):
        """Makes a PATCH request"""
        return self.open(
            HttpRequest(url, 'PATCH', query_params, data, headers))

    def delete(self, url, data=None, query_params=None, headers=None):
        """Makes a DELETE request"""
        return self.open(
            HttpRequest(url, 'DELETE', query_params, data, headers))

    def options(self, url, query_params=None, headers=None):
        """Makes an OPTIONS request"""
        return self.open(
            HttpRequest(url, 'OPTIONS', query_params, None, headers))

    def _compute_resp_size(self, response):
        return len(response.body)

    def _compute_req_size(self, request):
        return len(request.data or '')
