import sqlite3, os
from .exceptions import DatabaseError
from .abstractsql import AbstractSQLDB
from .abc import AbstractDBMS

class SqliteDB(AbstractSQLDB):
	"""
	SQLite3 adapter.

	The constuctor requires the filename of the
	database file.
	"""
	def __init__(self, filename):
		AbstractSQLDB.__init__(self)
		self.filename = filename

	def open(self):
		self._con = sqlite3.connect(self.filename)
	def close(self):
		self._con.close()

	def get_column_names(self, table):
		if(not table in self.get_table_names()):
			raise DatabaseError("unknown table: {}".format(table))
		cursor = self._con.cursor()
		cursor.execute("PRAGMA table_info({})".format(table))
		return [row[1] for row in cursor.fetchall()]

	def get_table_names(self):
		cursor = self._con.cursor()
		cursor.execute("SELECT name FROM sqlite_master WHERE type = \"table\"")
		return [row[0] for row in cursor.fetchall()]

class SqliteDBMS(AbstractDBMS):
	"""
	DBMS for SQLite files. All databases are files under ``path``.
	"""
	def __init__(self, path, filenames, inject = None, inject_as = None):
		AbstractDBMS.__init__(self)
		self._path = path
		self._filenames = filenames
		self.inject = inject
		self.inject_as = inject_as

	def dispatch_DB(self, db_name):
		if(not db_name in self._filenames):
			raise DatabaseError("unknown database")

		full_path = os.path.join(self._path, db_name)
		if(not os.path.exists(full_path)):
			raise DatabaseError("database does not exist")

		return SqliteDB(full_path) 
	
