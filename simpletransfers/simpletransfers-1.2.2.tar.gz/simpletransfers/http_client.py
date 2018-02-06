from __future__ import absolute_import, print_function, unicode_literals
"""
"""

import ctxlogger
import logging
import os
import re
import requests

from . import TransferException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class http_client(object):
    """
    Handle HTTP client transfers
    """

    def __init__(self,
        url,
        content_type='application/json',
        debug=False,
        headers={},
    ):

        self._address = url.lower()

        # content-type is such a common option it's given its own arg
        # so roll it in here
        self.headers = headers
        self.headers.update({'Content-Type': content_type})

    def __str__(self):
        return self._address

    def get(self, params={}):
        """
        Fetch data from a URL via a GET request

        params - HTTP parameters to submit with the request (default: {})
        """
        with ctxlogger.context('address', self._address):
            return self._request(requests.get, params)

    def put(self, data, name=None, params={}):
        """
        Put data to a URL via a POST request

        data - the data to send
        name - the filename of the data (currently ignored)
        params - HTTP parameters to submit with the request
        """
        with ctxlogger.context('address', self._address):
            return self._request(requests.post, params, data)

    def _request(self, method, params={}, data=None):
        """
        Send a request and handle the response
        """
        try:
            response = method(
                self._address,
                params=params,
                headers=self.headers,
                data=data,
            )
        except requests.exceptions.Timeout:
            return
        except requests.exceptions.RequestException as e:
            ctxlogger.exception(TransferException, str(e), orig_exc=e)

        if response.status_code != requests.codes.ok:
            ctxlogger.exception(
                TransferException, 
                '{} {}'.format(response.status_code, response.text),
            )

        filename = os.path.basename(self._address)

        # was a filename specified?
        try:
            disposition = response.headers['Content-Disposition']
        except KeyError:
            pass
        else:
            match = re.search('filename="([^"])"', disposition)
            if match:
                filename = match.group(1)

        return {filename: response.content}
