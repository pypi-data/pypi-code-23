"""
Web interface for databases using JSON requests.
"""

import cherrypy, json

import logging
logger = logging.getLogger(__name__)


def request_is_ok(request):
	try:
		if(not isinstance(request["database"], str)):
			logger.log("database name malformed")
			return False
		if(not isinstance(request["request"]["table"], str)):
			logger.log("table name malformed")
			return False
		if(not isinstance(request["request"]["parameters"], (list, dict))):
			logger.log("request parameters malformed")
			return False

		if(not request["request"]["operation"] in ("INSERT", "UPDATE", "DELETE", "SELECT")):
			logger.log("request operation malformed")
			return False

	except BaseException as e:
		logger.exception("in request_is_ok")
		return False

	return True

@cherrypy.expose
class DBInterface(object):
	"""
	Interface for databases.
	
	In the current version both GET and POST behave 
	the same way but this might be changed in the 
	future.
	
	This will try to fulfill the request 
	and return either nothing (Status = 204),
	plain text (Status = 200, Content-Type = text/plain)
	or JSON (Status = 200, Content-Type = application/json).

	On failure (Status = 400 or Status = 404) it will return
	a more or less helpful error message (Content-Type = text/plain).
	"""
	def __init__(self, dbms):
		self._dbms = dbms

	@cherrypy.tools.accept(media = "application/json")
	def GET(self, request):
		logger.info("GET; request = {}".format(request))

		try:
			cherrypy.response.headers["Content-Type"] = "text/plain"
			try:
				request = json.loads(request)
			except:
				logger.warn("could not parse request")
				cherrypy.response.headers["Status"] = 400
				return "request could not be parsed".encode("UTF-8")

			if(not request_is_ok(request)):
				cherrypy.response.headers["Status"] = 400
				return "malformed request".encode("UTF-8")

			result = self._dbms.handle_request(request)

			if(not result):
				cherrypy.response.headers["Status"] = 204
				return "".encode("UTF-8")

			if(isinstance(result, BaseException)):
				cherrypy.response.headers["Status"] = 404
				return str(result).encode("UTF-8")

			if(isinstance(result, (str, int, float, bool))):
				cherrypy.response.headers["Status"] = 200
				return str(result).encode("UTF-8")

			if(isinstance(result, (list, dict, tuple))):
				cherrypy.response.headers["Status"] = 200
				cherrypy.response.headers["Content-Type"] = "application/json"
				return json.dumps(result).encode("UTF-8")

		except BaseException as e:
			logger.exception("in GET")

		cherrypy.response.headers["Status"] = 404
		return "internal server error".encode("UTF-8")


		
	@cherrypy.tools.accept(media = "application/json")
	def POST(self, request):
		logger.info("GET; request = {}".format(request))

		try:
			cherrypy.response.headers["Content-Type"] = "text/plain"
			try:
				request = json.loads(request)
			except:
				logger.warn("could not parse request")
				cherrypy.response.headers["Status"] = 400
				return "request could not be parsed".encode("UTF-8")

			if(not request_is_ok(request)):
				cherrypy.response.headers["Status"] = 400
				return "malformed request".encode("UTF-8")

			result = self._dbms.handle_request(request)

			if(not result):
				cherrypy.response.headers["Status"] = 204
				return "".encode("UTF-8")

			if(isinstance(result, BaseException)):
				cherrypy.response.headers["Status"] = 404
				return str(result).encode("UTF-8")

			if(isinstance(result, (str, int, float, bool))):
				cherrypy.response.headers["Status"] = 200
				return str(result).encode("UTF-8")

			if(isinstance(result, (list, dict, tuple))):
				cherrypy.response.headers["Status"] = 200
				cherrypy.response.headers["Content-Type"] = "application/json"
				return json.dumps(result).encode("UTF-8")

		except BaseException as e:
			logger.exception("in POST")

		cherrypy.response.headers["Status"] = 404
		return "internal server error".encode("UTF-8")







