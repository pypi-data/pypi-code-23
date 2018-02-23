# -*- coding: utf-8 -*-
"""
iot.exceptions
~~~~~~~~~~~~~~~~~~~
This module contains the set of mqtt' exceptions.
    0: Connection successful
    1: Connection refused - incorrect protocol version
    2: Connection refused - invalid client identifier
    3: Connection refused - server unavailable
    4: Connection refused - bad username or password
    5: Connection refused - not authorised
    6-255: Currently unused.

"""
from urllib3.exceptions import HTTPError as BaseHTTPError


class IoTException(IOError):
	"""There was an ambiguous exception that occurred while handling your
	request.
	"""

	def __init__(self, *args, **kwargs):
		"""Initialize RequestException with `request` and `response` objects."""
		response = kwargs.pop('response', None)
		self.response = response
		self.request = kwargs.pop('request', None)
		if (response is not None and not self.request and
				hasattr(response, 'request')):
			self.request = self.response.request
		super(IoTException, self).__init__(*args, **kwargs)


class HTTPError(IoTException):
	"""An HTTP error occurred."""


class ConnectionError(IoTException):
	"""A Connection error occurred."""


class ProxyError(ConnectionError):
	"""A proxy error occurred."""


class SSLError(ConnectionError):
	"""An SSL error occurred."""


class Timeout(IoTException):
	"""The request timed out.
	Catching this error will catch both
	:exc:`~requests.exceptions.ConnectTimeout` and
	:exc:`~requests.exceptions.ReadTimeout` errors.
	"""


class ConnectTimeout(ConnectionError, Timeout):
	"""The request timed out while trying to connect to the remote server.
	Requests that produced this error are safe to retry.
	"""


class ReadTimeout(Timeout):
	"""The server did not send any data in the allotted amount of time."""


# Warnings


class IoTWarning(Warning):
	"""Base warning for Requests."""
	pass


class FileModeWarning(IoTWarning, DeprecationWarning):
	"""A file was opened in text mode, but Requests determined its binary length."""
	pass


class RequestsDependencyWarning(IoTWarning):
	"""An imported dependency doesn't match the expected version range."""
	pass
