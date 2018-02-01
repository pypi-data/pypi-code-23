from requests.exceptions import ConnectionError


class ValidationException(Exception):
	"""Custom ValidationException For """
	
	def __init__(self, message, key=None):
		super(ValidationException, self).__init__(message)
		self.key = key


class CoreException(Exception):
	"""Custom ValidationException For """
	
	def __init__(self, message):
		super(CoreException, self).__init__(message)


class ConsulException(ConnectionError):
	pass