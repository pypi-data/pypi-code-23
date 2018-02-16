import datetime
from .f import F

def toval (s, engine = "postgresql"):
	if isinstance (s, datetime.datetime):
		if engine == "postgresql":
			return "TIMESTAMP '" + s.strftime ("%Y-%m-%d %H:%M:%S") + "'"
		else:
			return "'" + s.strftime ("%Y-%m-%d %H:%M:%S") + "'"

	if isinstance (s, datetime.date):
		if engine == "postgresql":
			return "TIMESTAMP '" + s.strftime ("%Y-%m-%d %H:%M:%S") + "'"
		else:
			return "'" + s.strftime ("%Y-%m-%d %H:%M:%S") + "'"		
	
	if s is None:
		return "NULL"	
	
	if isinstance (s, bool):
		return s == True and 'true' or 'false'
		
	if isinstance (s, (float, int, F)):
		return str (s)
		
	return "'" + s.replace ("'", "''") + "'"

class D:
	def __init__ (self, **data):
		self._feed = data
		self._columns = list (self._feed.keys ())
		self._encoded = False
	
	def encode (self, engine):
		if self._encoded:
			return
		_data = {}
		for k, v in self._feed.items ():
			_data [k] = toval (v, engine)
		self._feed = _data
		self._encoded = True
		
	@property
	def columns (self):	
		return ", ".join (self._columns)
	
	@property
	def values (self):		
		return ", ".join ([self._feed [c] for c in self._columns])
	
	@property
	def pairs (self):		
		return ", ".join (["{} = {}".format (c, self._feed [c]) for c in self._columns])
		