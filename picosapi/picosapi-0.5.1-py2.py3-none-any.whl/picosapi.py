"""
Picos API Module
Requires Python 3

The following Python 3 definitions provide a simple interface into making external calls to
Picos. 

Braden Hitchcock
March 1, 2018
"""
import requests
import pprint
import sys


__configuration = {
	"host": "localhost",
	"port": 8080
}

__pp = pprint.PrettyPrinter(indent=4, width=100)


class EventURL(object):
	"""Simple class that holds information about an event url targeting a pico engine. By default,
	this URL will use the module configured `host` and `port` configuration values when
	building a URL to use in an HTTP request. This is so that we can provide a more dynamic API.
	
	If the developer sets the `static` param to `True`, then the URL will store the current
	(or provided) values for the host and port internally so that even if the developer changes the 
	configuration later in the program, this instance will still have the same host and port"""
	def __init__(self, eci, event_name, event_domain, event_type, static=False, host=None, port=None):
		self.static = static
		self.host = host
		self.port = port
		self.name = event_name
		self.eci = eci
		self.domain = event_domain
		self.type = event_type

	def __str__(self):
		url_base = request_url_base() if not self.static else "http://%s:%d" % (self.host, self.port)
		return "%s/sky/event/%s/%s/%s/%s" % (url_base, self.eci, self.name, 
										 self.domain, self.type)


class ApiURL(object):
	"""Simple class that holds information about an API call url that targets the Sky Cloud API on
	the pico engine. By default, this URL will use the module configured `host` and `port` 
	configuration values when building a URL to use in an HTTP request. This is so that we can 
	provide a more dynamic API.
	
	If the developer sets the `static` param to `True`, then the URL will store the current
	(or provided) values for the host and port internally so that even if the developer changes the 
	configuration later in the program, this instance will still have the same host and port"""
	def __init__(self, eci, ruleset_id, function, static=False, host=None, port=None):
		self.static = static
		self.host = host
		self.port = port
		self.ruleset_id = ruleset_id
		self.eci = eci
		self.function = function

	def __str__(self):
		url_base = request_url_base() if not self.static else "http://%s:%d" % (self.host, self.port)
		return "%s/sky/cloud/%s/%s/%s" % (request_url_base(), self.eci, self.ruleset_id, self.function)


class SuccessResponse(object):
	"""Holds response information when an HTTP request method is successful. The code lets us
	decide how to respond to the result with the content provided by the respond"""
	def __init__(self, code, response):
		self.code = code
		self.content = response

	def __str__(self):
		return "[SUCCESS] :: Response Code: %d --\n%s" % (self.code, p_print(self.content))


class ErrorResponse(object):
	"""Holds response information when an HTTP request method fails or does not return a code
	specified by the developer as acceptable"""
	def __init__(self, message, code, content):
		self.code = code
		self.content = content	
		self.message = message

	def __str__(self):
		return "[ERROR] %s :: Response Code: %d --\n%s" % (self.message, self.code, 
															p_print(self.content))


def get_config(key, default=None):
	"""Provides access to module configuration values.
	:param key: the key representing the value
	:param default: optional default return value if the key is not in the configuration"""
	return __configuration.get(key, default)


def set_config(key, value):
	"""Sets a configuration value in the module configuration map. If the key is not present, it
	will create an entry.
	:param key: the key of the value to insert or update
	:param value: the value to associate with the key in the configuration map"""
	__configuration[key] = value


def request_url_base():
	"""Constructs the default HTTP URL base according to module configuration"""
	return "http://%s:%d" % (__configuration["host"], __configuration["port"])


def p_print(obj):
	"""Pretty-prints the provided object with a max width of 100 and indentations of 4 characters
	:param obj: the object to print in pretty print format"""
	return __pp.pformat(obj)


def event_url(eci, event_name, event_domain, event_type, static=False, host=None, port=None):
	"""Creates and returns a new EventURL object containing information that builds the URL to
	connect to for HTTP requests
	:param eci: the event channel identifier (ECI) of the Pico to raise an event on
	:param event_name: the name/id of the event to raise
	:param event_domain: the domain of the event
	:param event_type: the type of the event
	:param static: (optional, default False) if True, allows the generated URL object's
				   host and port to be modified
	:param host: (optional, default None) alternately specified host IP address
	:param port: (option, default None) alternately specified host port
	:returns: an object representing the URL
	:rtype: EventURL"""
	if static:
		host = host if not static and host is not None else __configuration["host"]
		port = port if not static and port is not None else __configuration["port"]
		return EventURL(eci, event_name, event_domain, event_type, static, host, port)
	else:
		return EventURL(eci, event_name, event_domain, event_type)


def api_url(eci, ruleset_id, api_function, static=False, host=None, port=None):
	"""Creates and returns a new ApiURL object containing information that builds the URL to
	connect to for HTTP requests
	:param eci: the event channel identifier (ECI) of the Pico to raise an event on
	:param ruleset_id: the id of the ruleset the API function belongs to on the Pico
	:param api_function: the name of the function in the ruleset to call
	:param static: (optional, default False) if True, allows the generated URL object's
				   host and port to be modified
	:param host: (optional, default None) alternately specified host IP address
	:param port: (option, default None) alternately specified host port
	:returns: an object representing the API URL
	:rtype: ApiURL"""
	if static:
		host = host if not static and host is not None else __configuration["host"]
		port = port if not static and port is not None else __configuration["port"]
		return ApiURL(eci, ruleset_id, api_function, static, host, port)
	else:
		return ApiURL(eci, ruleset_id, api_function)


def get(purl, params=None, headers={}, ok_responses=[200]):
	"""HTTP GET request
	:param purl: a Pico URL, formatted using the EventURL and ApiURL objects
	:param params: a map of key-value pairs representing query string parameters
	:param headers: additional HTTP headers to include in the request
	:param ok_responses: a list of HTTP response codes that don't trigger an error
	:return: a boolean, response object pair - (True, SuccessResponse) or (False, ErrorResponse)
	"""
	try:
		r = requests.get(str(purl), params=params, headers=headers)
		if r.status_code in ok_responses:
			return True, SuccessResponse(r.status_code, r.json())
		else:
			return False, ErrorResponse("GET failed", r.status_code, r.json())
	except Exception as e:
		return False, ErrorResponse("caught exception", 400, {"message": str(e) })


def post(purl, data={}, headers={}, ok_responses=[200]):
	"""HTTP POST request
	:param purl: a Pico URL, formatted using the EventURL and ApiURL objects
	:param data: a map representing the JSON formatted data to send
	:param headers: additional HTTP headers to include in the request
	:param ok_responses: a list of HTTP response codes that don't trigger an error
	:return: a boolean, response object pair - (True, SuccessResponse) or (False, ErrorResponse)
	"""
	try:
		r = requests.post(str(purl), json=data, headers=headers)
		if r.status_code in ok_responses:
			return True, SuccessResponse(r.status_code, r.json())
		else:
			return False, ErrorResponse("POST failed", r.status_code, r.json())
	except Exception as e:
		return False, ErrorResponse("caught exception", 400, {"message": str(e) })


def put(purl, data={}, headers={}, ok_responses=[200]):
	"""HTTP PUT request
	:param purl: a Pico URL, formatted using the EventURL and ApiURL objects
	:param data: a map representing the JSON formatted data to send
	:param headers: additional HTTP headers to include in the request
	:param ok_responses: a list of HTTP response codes that don't trigger an error
	:return: a boolean, response object pair - (True, SuccessResponse) or (False, ErrorResponse)
	"""
	try:
		r = requests.put(str(purl), json=data, headers=headers)
		if r.status_code in ok_responses:
			return True, SuccessResponse(r.status_code, r.json())
		else:
			return False, ErrorResponse("PUT failed", r.status_code, r.json())
	except Exception as e:
		return False, ErrorResponse("caught exception", 400, {"message": str(e) })


def delete(url, headers={}, ok_responses=[200]):
	"""HTTP DELETE request
	:param purl: a Pico URL, formatted using the EventURL and ApiURL objects
	:param headers: additional HTTP headers to include in the request
	:param ok_responses: a list of HTTP response codes that don't trigger an error
	:return: a boolean, response object pair - (True, SuccessResponse) or (False, ErrorResponse)
	"""
	return None