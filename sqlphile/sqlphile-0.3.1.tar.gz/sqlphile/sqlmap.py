from . import sql
import os
import re

class SQLMap:
	def __init__ (self, map = None, auto_reload = False, engine = "postgresql"):
		self._map = map
		self._auto_reload = auto_reload
		self._engine = engine
		self._version = "1.0"
		self._sqls = {}
		self._last_modifed = 0
		if self._map:
			self._read_from_file ()
	
	def __getattr__ (self, name):		
		self._reloaderble () and self._read_from_file ()
		if self._sqls.get (name) is None:
			raise AttributeError ("SQL template '{}' not found".format (name))
		return sql.SQLTemplateRederer (self._sqls.get (name), self._engine)
		
	def _reloaderble (self):
		return self._map and self._auto_reload and self._last_modifed != os.path.getmtime (self._map)
		
	def _read_from_file (self):
		self._last_modifed = os.path.getmtime (self._map)
		with open (self._map) as f:
			self._read_from_string (f.read ())
	
	RX_NAME	= re.compile ("\sname\s*=\s*['\"](.+?)['\"]")
	RX_VERSION	= re.compile ("\sversion\s*=\s*['\"](.+?)['\"]")
	def _read_from_string (self, data):
		self._sqls = {}
		
		current_name = None
		current_data = []
		for line in data.split ("\n"):
			if not line.strip ():
				continue
			
			if line.startswith ("<sqlmap "):
				m = self.RX_VERSION.search (line)
				if m:					
					self._version = m.group (1)
				
			elif line.startswith ("</sql>"):
				if not current_name:
					raise ValueError ("unexpected end tag </sql>")
				self._sqls [current_name] = "\n".join (current_data)
				current_name, current_data = None, []				 
			
			elif line.startswith ("<sql "):
				m = self.RX_NAME.search (line)
				if not m:
					raise ValueError ("name attribute required")
				current_name = m.group (1)
			
			elif current_name:
				current_data.append (line.strip ())

