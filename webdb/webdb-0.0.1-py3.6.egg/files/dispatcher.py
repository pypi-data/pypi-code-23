"""
File dispatchers for serving files for web applications.
"""

from abc import abstractmethod, ABCMeta
from .file import FileOverlay
import os
import logging

logger = logging.getLogger(__name__)

class AbstractFileDispatcher(metaclass = ABCMeta):
	@abstractmethod
	def dispatch_file(self, path, *args):
		"""
		Dispatch the file. This **must always** return 
		a ``FileOverlay``. Even if the file must not be accessed,
		or does not exist. In this case the ``modes`` must be emtpy.
		"""
		pass
	def cleanup_path(self, path):
		"""
		Clean up the path. Remove any ".."s and a leading "/".

		``dispatch_file`` **must** call this method before actually dispatching the
		file.
		"""
		if(path[0] == "/"):
			path = path[1:]
		return path.replace("..", "")


class UserFileDispatcher(AbstractFileDispatcher):
	"""
	This file dispatcher has a seperated path for
	every user. The user is allowed to do anything
	in this path (read, write, create, create parents).

	Only use this for "reliable" clients.
	"""
	def __init__(self, root):
		self._root = root

	def dispatch_file(self, path, username):
		path = self.cleanup_path(path)
		root = os.path.join(self._root, username)
		return FileOverlay(path, root, "rwcp", path)



class QuotaUserFileDispatcher(UserFileDispatcher):
	"""
	This file dispatcher has a seperated path for
	every user. The user is allowed to do anything
	in this path (read, write, create, create parents).

	This file dispatcher will refuse changes, if a quota has
	been exceeded.

	Only use this for "semi reliable" clients.
	"""
	def __init__(self, root, quota):
		UserFileDispatcher.__init__(self, root)
		self._quota = quota

	def dispatch_file(self, path, username):
		path = self.cleanup_path(path)
		root = os.path.join(self._root, username)
		current_size = 0
		# FIXME:
		# this is extremely inefficient. 
		# I will have to figure out a safe 
		# way of buffering the size.
		for directory in os.walk(root):
			for f in directory[1]:
				if(not os.path.isfile(f)):
					continue
				current_size += os.stat(f).st_size
		return FileOverlay(path, root, "rwcp", path, self._quota - current_size)


class SQLFileDispatcher(AbstractFileDispatcher):
	"""
	This is a nice dispatcher for controlled environments,
	such as sharing files between users or a limited set of 
	files.

	The dispatcher looks up the files in a database, dispatchs the real
	path and returns the according FileOverlay.

	The commands for creating the tables are::

		CREATE TABLE files(path text UNIQUE,
				id integer PRIMARY KEY AUTOINCREMENT,
				max_size integer);

		CREATE TABLE access(file_id integer,
				username text,
				modes text);

		CREATE TABLE nicknames(name text PRIMARY KEY,
				file_id integer);

		CREATE INDEX access_index ON access(file_id);

		CREATE TABLE root(root text UNIQUE);


	**NOTE**: This dispatcher does NOT allow creating files.

	**NOTE**: if ``max_size`` is ``-1`` it will be interpreted as
		"has no max size".
		
	"""

	def __init__(self, db_connection):
		self._db = db_connection
		cursor = self._db.cursor()
		try:
			cursor.execute("SELECT root from root")
			self._root = cursor.fetchone()[0]
		except: 
			pass
		if(not self._root):
			logger.error("Root directory is not set. " \
				"You have forgotten to insert the absolute root path "\
				"into the database.")
			raise IOError("root directory is not set")

	def dispatch_file(self, nickname, username):
		"""
		This method looks up the file in the sqlite database and
		resolves the real path, the access rights and the modes

		"""

		cursor = self._db.cursor()

		cursor.execute("SELECT file_id FROM nicknames WHERE name = ?", [nickname])
		result = cursor.fetchone()
		if(not result):
			raise IOError("unknown file")
		file_id = result[0]

		cursor.execute("SELECT path, max_size FROM files WHERE id = ?", [file_id])

		result = cursor.fetchone()
		if(not result):
			# XXX:
			# This is bad. 
			# The database is desynced (most propably a DELETE Anomaly.).
			# However the user should most propably not know about this.
			logger.error("XXX: file database is desynced. This is most propably a DELETE anomaly" \
					" there is a nickname pointing to file_id={}, but this file_id is not" \
					" in files.".format(file_id))
			raise IOError("unknown file")

		path, maxsize = result

		if(maxsize == -1):
			max_size = float("inf")

		cursor.execute("SELECT modes FROM access WHERE file_id = ? AND username = ?", [file_id, username])
		result = cursor.fetchone()

		if(not result):
			modes = ""
		else:
			modes = result[0]


		# Create and create parents is not supported 
		# this feature will most probably never be implemented.
		# How does the system what files the user may create?
		modes = modes.replace("c", "").replace("p", "")

		logger.info("dispatched: path: {}, root: {}, modes: {}, nickname: {}, maxsize: {}".format(
				path, self._root, modes, nickname, max_size))
		return FileOverlay(path, self._root, modes, nickname, max_size) 
