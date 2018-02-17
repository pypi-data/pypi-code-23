from . import db3
import psycopg2
from aquests.dbapi import DB_PGSQL

class open (db3.open):
	def __init__ (self, dbname, user, password, host = '127.0.0.1', port = 5432):
		self.conn = psycopg2.connect (host=host, dbname=dbname, user=user, password=password, port = port)
		self.__init (DB_PGSQL)		
		
	def field_names (self):
		return [x.name for x in self.description]
		
		