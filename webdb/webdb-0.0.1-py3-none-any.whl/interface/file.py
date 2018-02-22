"""
Web interface for file access.
"""

import cherrypy
import logging

logger = logging.getLogger(__name__)


@cherrypy.expose
class DispatchedFile(object):
	"""
	This is the class that actually serves a file.
	See the documentation of FileInterface, about the usage.
	"""
	def __init__(self, dispatcher, inject, nickname):
		self._dispatcher = dispatcher
		self._inject = inject
		self._nickname = nickname
		self._file = None

	def before_operation(self):
		self._file = self._dispatcher.dispatch_file(self._nickname, self._inject())
	
	def GET(self, offset = 0, chunk_size = 0):
		self.before_operation()

		try:
			offset = int(offset)
		except:
			cherrypy.response.headers["Status"] = 400
			return b"cannot convert {} to int".format(offset)

		try:
			chunk_size = int(chunk_size)
		except:
			cherrypy.response.headers["Status"] = 400
			return b"cannot convert {} to int".format(chunk_size)

		
		try: 
			file_part = self._file.get_file_part(offset, chunk_size)
		except Exception as e:
			cherrypy.response.headers["Status"] = 404
			logger.error(e, exc_info = True)
			return str(e).encode("UTF-8")

		cherrypy.response.headers["Status"] = 200
		cherrypy.response.headers["Content-Type"] = "application/octet-stream"

		return file_part

	def POST(self, offset = 0):
		self.before_operation()
		try:
			offset = int(offset)
		except:
			cherrypy.response.headers["Status"] = 400
			return b"cannot convert {} to int".format(offset)

		try:
			self._file.copy_file_part(offset, cherrypy.request.body)
		except Exception as e:
			cherrypy.response.headers["Status"] = 404
			logger.error(e, exc_info = True)
			return str(e).encode("UTF-8")

		cherrypy.response.headers["Status"] = 204
			
		

	def DELETE(self, truncate = None):
		self.before_operation()
		try:
			truncate = int(truncate)
		except:
			truncate = None

		try:
			if(truncate != None):
				self._file.truncate(truncate)
			else:
				self._file.remove_file()
		except Exception as e:
			cherrypy.response.headers["Status"] = 404
			logger.error(e, exc_info = True)
			return str(e).encode("UTF-8")

		cherrypy.response.headers["Status"] = 204
	
	def PUT(self):
		self.before_operation()
		try:
			self._file.create_file()
		except Exception as e:
			cherrypy.response.headers["Status"] = 404
			logger.error(e, exc_info = True)
			return str(e).encode("UTF-8")

		cherrypy.response.headers["Status"] = 204


class FileInterface(object):
	"""
	Serves files. 
	A HTTP POST will write (a part of ) the file,
	HTTP GET will return (a part of) the file.

	**Interface:**

	Files are associated with a path. Assuming that the interface
	is mounted under ``/files``, it will dispatch ``/files/foo/bar.baz``
	to the path ``foo/bar.baz``. This path is passed to the dispatcher
	instance and the actual FileOverlay will be dispatched.

	One can delete the file using HTTP DELETE. If the argument ``?truncate=<bytes>``
	is supplied, the file will be truncated to ``<bytes>``. 
	**NOTE**: if ``<bytes>`` cannot be converted to an integer, the file
	will be deleted.

	The file can be created expicily by using HTTP PUT.

	One can receive (a part) of a file using HTTP GET. If ``offset``
	is provided the file part will start at byte ``offset``. If
	``chunk_size`` is provided at most ``chunk_size`` bytes will be
	returned.

	HTTP POST will set (a part) of a file. If ``offset`` is provided
	the file part will be written at ``offset``. Content-Type must be
	``application/octet-stream``.

	If the POST/DELETE/PUT request succeed Status 204 will be set.
	If GET succeeds Status 200 will be set and the (binary) file content
	will be returned. Content-Type in this case is ``application/octet-stream``.

	If any request fails Status 404 will be set and a (more or less) helpful
	error message will be returned. If an argument cannot be parsed properly
	Status 400 will be set and an error message will be returned.

	The constructor argument ``inject`` is a callable that returns the second
	argument of the dispatcher's dispatch_file. Usually this will be something
	like ``lambda: cherrypy.session["username"]``.

	XXX:
	***NOTE***:

	Youn MUST (!) add ``{'request.dispatch': cherrypy.dispatch.MethodDispatcher()}``
	to your application config. If you forget that cherrypy will not be able to
	dispatch the methods properly.
	"""
	def __init__(self, dispatcher, inject):
		self._dispatcher = dispatcher
		self._inject = inject

	def _cp_dispatch(self, vpath):
		nickname = "/".join(vpath)

		vpath.clear()
		return DispatchedFile(self._dispatcher, self._inject, nickname)

