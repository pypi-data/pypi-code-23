from __future__ import absolute_import, print_function, unicode_literals
"""
"""

import contextlib
import ctxlogger
import logging
import suds
import re
import urllib2

from . import TransferException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class soap(object):

    _wsdl = ''
    _client = None

    """
    Make remote SOAP calls
    """
    def __init__(self, wsdl, headers = None, timeout = 10):
        """
        wsdl - the WDSL for this connection
        """
        self._wsdl = wsdl
        self._client = suds.client.Client(self._wsdl, timeout = timeout)
        if headers:
            self._client.set_options(soapheaders = headers)

    def __str__(self):
        return 'soap://{}'.format(self._wsdl)

    def put(self, data, name):
        """
        data - the message to send to the remote method
        name - the name of the method to call
        """
        with contextlib.nested(
            ctxlogger.context('service', str(self._wsdl)),
            ctxlogger.context('function', name)
        ):
            try:
                remote_func = getattr(self._client.service, name)
            except AttributeError as e:
                ctxlogger.exception(
                    TransferException, 'Unrecognised Function', orig_exc = e
                )

            try:
                return remote_func(data)
            except suds.WebFault as e:
                ctxlogger.exception(TransferException, str(e), orig_exc = e)
            except urllib2.URLError as e:
                if 'timed out' in str(e):
                    return
                ctxlogger.exception(TransferException, str(e), orig_exc = e)

    def get(self, name):
        """
        name - the remote method to call
        """
        return self.put(None, name)
