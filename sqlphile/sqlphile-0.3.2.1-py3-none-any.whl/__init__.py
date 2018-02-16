import os
import re
from . import sql
from .sql import SQL, SQLTemplateRederer, SQLComposer
from .sqlmap import SQLMap
from .q import Q, V
from .d import D
from .f import F
from . import db3, pg2
from .utils import *
 
__version__ = "0.3.2.1"

class SQLPhile:
	def __init__ (self, dir = None, auto_reload = False, engine = "postgresql"):
		self._dir = dir
		self._auto_reload = auto_reload
		self._engine = engine
		self._ns = {}
		self._dir and self._load_sqlmaps ()
	
	def __resolve (self, table, alias):
		return alias and (table + " AS " + alias) or table
		
	def insert (self, table, alias = None):
		return sql.SQLComposer ("INSERT INTO " + self.__resolve (table, alias) + " ({_columns}) VALUES ({_values})", self._engine)
		
	def update (self, table, alias = None):		
		return sql.SQLComposer ("UPDATE " + self.__resolve (table, alias) + " SET {_pairs}", self._engine)
		
	def select (self, table, alias = None):
		return sql.SQLComposer ("SELECT {select} FROM " + self.__resolve (table, alias), self._engine).feed (select = "*")
		
	def delete (self, table, alias = None):
		return sql.SQLComposer ("DELETE FROM " + self.__resolve (table, alias), self._engine)
		
	def template (self, template):
		return sql.SQLTemplateRederer (template, self._engine)
		
	def __getattr__ (self, name):
		try:
			return self._ns [name]
		except KeyError:
			return getattr (self._ns ["default"], name)
	
	def _load_sqlmaps (self):
		for fn in os.listdir (self._dir):
			if fn[0] == "#":
				continue			
			ns = fn.split (".") [0]
			if ns == "ops":
				raise NameError ('ops cannot be used SQL map file name')
			self._ns [ns] = SQLMap (os.path.join (self._dir, fn), self._auto_reload, self._engine)
