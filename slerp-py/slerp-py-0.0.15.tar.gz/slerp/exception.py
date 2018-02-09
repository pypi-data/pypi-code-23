from requests.exceptions import ConnectionError


class ValidationException(Exception):
	"""Custom ValidationException For """
	
	def __init__(self, message, key=None):
		self.message = message
		self.key = key
		super(ValidationException, self).__init__(message)


class CoreException(Exception):
	"""Custom ValidationException For """
	
	def __init__(self, message):
		self.message = message
		super(CoreException, self).__init__(message)


class ConsulException(ConnectionError):
	pass
