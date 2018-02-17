import sqlite3
import json
import zlib
import sqlphile
from aquests.lib import attrdict
from aquests.dbapi import DB_SQLITE3

class open:
	def __init__ (self, path):		
		self.conn = sqlite3.connect (path, check_same_thread = False)
		self.__init (DB_SQLITE3)
	
	def __init (self, engine):	
		self.create_cursor ()
		self.sqlphile = sqlphile.SQLPhile (engine = engine)
	
	def create_cursor (self):	
		self.cursor = self.c = self.conn.cursor ()
	
	def __enter__ (self):
		return self
	
	def __exit__ (self, type, value, tb):
		self.c.close ()
		self.conn.close ()
		
	def __getattr__ (self, name):
		try: 
			return getattr (self.c, name)			
		except AttributeError:
			return getattr (self.sqlphile, name)
	
	def commit (self):	
		return self.conn.commit ()
	
	def rollback (self):	
		return self.conn.rollback ()	

	def serialize (self, obj):
		return zlib.compress (json.dumps (obj).encode ("utf8"))	
	
	def deserialize (self, data):
		return json.loads (zlib.decompress (data).decode ('utf8'))
	
	def blob (self, obj):
		return sqlite3.Binary (obj)
	
	def field_names (self):
		return [x [0] for x in self.description]
		
	def as_dict (self, row, field_names = None):		
		return attrdict.AttrDict (dict ([(f, row [i]) for i, f in enumerate (field_names or self.field_names ())]))
	
	def fetchone (self, as_dict = False):
		return self.fetchmany (1, as_dict)[0]
		
	def fetchall (self, as_dict = False):
		return self.fetchmany (0, as_dict)
	
	def fetchmany (self, limit, as_dict = False):
		rows = limit and self.cursor.fetchmany (limit) or self.cursor.fetchall ()
		if not as_dict:
			return rows		
		field_names = self.field_names ()
		return [self.as_dict (row, field_names) for row in rows]
	
	def execute (self, sql, *args, **kargs):
		return self.cursor.execute (str (sql), *args, **kargs)
	
		 		
		