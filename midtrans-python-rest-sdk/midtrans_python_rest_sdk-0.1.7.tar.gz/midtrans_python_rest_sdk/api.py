from __future__ import division

import base64
import datetime
import requests
import json
import logging
import os

from .util import join_url, merge_dict
from .exceptions import *
from .config import __version__, __endpoint_map__

log = logging.getLogger(__name__)


class Api(object):

    def __init__(self, options=None, **kwargs):
        """Create API object

        Usage::

            >>> import paypalrestsdk
            >>> api = paypalrestsdk.Api(mode="sandbox", server_key='SERVER_KEY')
        """
        kwargs = merge_dict(options or {}, kwargs)

        self.mode = kwargs.get("mode", "sandbox")

        if self.mode != "live" and self.mode != "sandbox":
            raise InvalidConfig("Configuration Mode Invalid", "Received: %s" % (self.mode), "Required: live or sandbox")

        self.endpoint = kwargs.get("endpoint", self.default_endpoint())
        # Mandatory parameter, so not using `dict.get`
        self.server_key = kwargs["server_key"]
        self.proxies = kwargs.get("proxies", None)

        self.options = kwargs

    def default_endpoint(self):
        return __endpoint_map__.get(self.mode)

    def basic_auth(self):
        """Find basic auth, and returns base64 encoded
        """
        credentials = "%s:" % (self.server_key)
        return base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    def request(self, url, method, body=None):
        """Make HTTP call, formats response and does error handling. Uses http_call method in API class.

        Usage::

            >>> api.request("https://api.sandbox.paypal.com/v1/payments/payment?count=10", "GET", {})
            >>> api.request("https://api.sandbox.paypal.com/v1/payments/payment", "POST", "{}", {} )

        """

        http_headers = self.headers()

        try:
            return self.http_call(url, method, data=json.dumps(body), headers=http_headers)

        # Format Error message for bad request
        except BadRequest as error:
            return {"error": json.loads(error.content)}

    def http_call(self, url, method, **kwargs):
        """Makes a http call. Logs response information.
        """
        log.info('Request[%s]: %s' % (method, url))

        if self.mode.lower() != 'live':
            request_headers = kwargs.get("headers", {})
            request_body = kwargs.get("data", {})
            log.debug("Level: " + self.mode)
            log.debug('Request: \nHeaders: %s\nBody: %s' % (
                str(request_headers), str(request_body)))
        else:
            log.info(
                'Not logging full request/response headers and body in live mode for compliance')

        start_time = datetime.datetime.now()
        response = requests.request(
            method, url, proxies=self.proxies, **kwargs)
        duration = datetime.datetime.now() - start_time
        log.info('Response[%d]: %s, Duration: %s.%ss.' % (
            response.status_code, response.reason, duration.seconds, duration.microseconds))

        if self.mode.lower() != 'live':
            log.debug('Headers: %s\nBody: %s' % (
                str(response.headers), str(response.content)))

        return self.handle_response(response, response.content.decode('utf-8'))

    def handle_response(self, response, content):
        """Validate HTTP response
        """
        status = int(json.loads(content).get('status_code'))
        if status in (301, 302, 303, 307):
            raise Redirection(response, content)
        elif 200 <= status <= 299:
            return json.loads(content) if content else {}
        elif status == 400:
            raise BadRequest(response, content)
        elif status == 401:
            raise UnauthorizedAccess(response, content)
        elif status == 403:
            raise ForbiddenAccess(response, content)
        elif status == 404:
            raise ResourceNotFound(response, content)
        elif status == 405:
            raise MethodNotAllowed(response, content)
        elif status == 406:
            raise NotAcceptable(response, content)
        elif status == 409:
            raise ResourceConflict(response, content)
        elif status == 410:
            raise ResourceGone(response, content)
        elif status == 422:
            raise ResourceInvalid(response, content)
        elif 401 <= status <= 499:
            raise ClientError(response, content)
        elif 500 <= status <= 599:
            raise ServerError(response, content)
        else:
            raise ConnectionError(
                response, content, "Unknown response code: #{response.code}")

    def headers(self, headers=None):
        """Default HTTP headers
        """
        return {
            "Authorization": self.basic_auth(),
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get(self, action):
        """Make GET request

        Usage::

            >>> api.get("v1/payments/payment?count=1")
            >>> api.get("v1/payments/payment/PAY-1234")
        """
        return self.request(join_url(self.endpoint, action), 'GET')

    def post(self, action, params=None):
        """Make POST request

        Usage::

            >>> api.post("v1/payments/payment", { 'indent': 'sale' })
            >>> api.post("v1/payments/payment/PAY-1234/execute", { 'payer_id': '1234' })

        """
        return self.request(join_url(self.endpoint, action), 'POST', body=params or {})

    def put(self, action, params=None):
        """Make PUT request

        Usage::

            >>> api.put("v1/invoicing/invoices/INV2-RUVR-ADWQ", { 'id': 'INV2-RUVR-ADWQ', 'status': 'DRAFT'})
        """
        return self.request(join_url(self.endpoint, action), 'PUT', body=params or {})

    def patch(self, action, params=None):
        """Make PATCH request

        Usage::

            >>> api.patch("v1/payments/billing-plans/P-5VH69258TN786403SVUHBM6A", { 'op': 'replace', 'path': '/merchant-preferences'})
        """
        return self.request(join_url(self.endpoint, action), 'PATCH', body=params or {})

    def delete(self, action):
        """Make DELETE request
        """
        return self.request(join_url(self.endpoint, action), 'DELETE')

__api__ = None


def default():
    """Returns default api object and if not present creates a new one
    By default points to developer sandbox
    """
    global __api__
    if __api__ is None:
        try:
            server_key = os.environ["MIDTRANS_SERVER_KEY"]
        except KeyError:
            raise MissingConfig("Required MIDTRANS_SERVER_KEY. \
                Refer https://github.com/paypal/rest-api-sdk-python#configuration")

        __api__ = Api(mode=os.environ.get(
            "MIDTRANS_ENVIRONMENT", "sandbox"), server_key=server_key)
    return __api__


def set_config(options=None, **config):
    """Create new default api object with given configuration
    """
    global __api__
    __api__ = Api(options or {}, **config)
    return __api__

configure = set_config
