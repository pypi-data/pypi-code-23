from . import utils
from .q import Q, V, batch
from .d import toval, D

class SQL:
	def __init__ (self, template, engine = "postgresql"):	
		self._template = template		
		self._engine = engine
		self._filters = []
		self._limit = 0
		self._offset = 0
		self._order_by = None
		self._group_by = None
		self._having = None
		self._returning = None		
		self._feed = {}
		self._data = {}
		
	@property
	def query (self):
		return self.as_sql ()
	
	def render (self):
		return self.as_sql ()
		
	def __str__ (self):
		return self.as_sql ()
	
	def __getitem__(self, key):
		key.start and self.offset (key.start)
		if key.stop:
			self.limit (key.stop - (key.start or 0))
		return self
		
	def exclude (self, *Qs, **filters):
		for q in Qs + tuple (batch (**filters)):
			if q:
				q.render (self._engine)
				self._filters.append ("NOT (" + str (q) + ")")
		return self
	
	def returning	(self, *args):
		self._returning = "RETURNING " + ", ".join (args)
		return self
	
	def filter (self, *Qs, **filters):
		for q in Qs + tuple (batch (**filters)):
			if q:
				q.render (self._engine)
				self._filters.append (str (q))		
		return self
	
	def having (self, cond):
		self._having = "HAVING " + cond
		return self
		
	def order_by (self, *by):
		self._order_by = utils.make_orders (by)
		return self
	
	def group_by (self, *by):
		self._group_by = utils.make_orders (by, "GROUP")
		return self
		
	def limit (self, val):
		self._limit = "LIMIT {}".format (val)
		return self
	
	def offset (self, val):
		self._offset = "OFFSET {}".format (val)
		return self
				
	def data (self, **karg):
		for k, v in karg.items ():
			if isinstance (v, D):
				self.addD (k, v)			
			else:	
				self._data [k] = toval (v, self._engine)
		return self
		
	def feed (self, **karg):
		for k, v in karg.items ():
			if isinstance (v, D):
				self.addD (k, v)
			else:			
				# Q need str()
				if isinstance (v, Q) and not v:
					# for ignoring
					v = "1 = 1"					
				elif isinstance (v, (V, Q)):
					v.render (self._engine)					
				self._feed [k] = str (v)
		return self
	
	def as_sql (self):
		raise NotImplementedError
	

class SQLTemplateRederer (SQL):
	def __call__ (self, **karg):
		return self.feed (**karg)
	
	def addD (self, prefix, D_):
		D_.encode (self._engine)
		self._data [prefix + "_columns"] = D_.columns
		self._data [prefix + "_values"] = D_.values
		self._data [prefix + "_pairs"] = D_.pairs
	
	def as_sql (self):
		data = utils.D (**self._data)
		self._feed.update (self._data)
		
		return self._template.format (
			_filters = " AND ".join ([f for f in self._filters if f]),
			_limit = self._limit,
			_offset = self._offset,
			_order_by = self._order_by,
			_group_by = self._group_by,
			_having = self._having,
			_columns = data.columns,
			_values = data.values,
			_pairs = data.pairs,
			_returning = self._returning,
			**self._feed
		)


class SQLComposer (SQL):	
	def __init__ (self, template, engine = "postgresql"):	
		SQL.__init__ (self, template, engine)
		self._joins = []
		
	def get (self, *columns):
		self._feed ["select"] = ", ".join (columns)
		return self
	
	def _join	(self, jtype, obj, alias, *Qs, **filters):
		_filters = []
		for q in Qs + tuple (batch (**filters)):
			if q:
				q.render (self._engine)
				_filters.append (str (q))				
		_filters = " AND ".join ([f for f in _filters if f])
		if not isinstance (obj, str):
			# SQL
			obj = "({})".format (obj)
		self._joins.append (
			"{} {} AS {} ON {}".format (jtype, obj, alias, _filters)
		)
		return self
	
	def from_	(self, obj, alias, *Qs, **filters):
		return self._join ("FROM", obj, alias, *Qs, **filters)
	
	def join	(self, obj, alias, *Qs, **filters):
		return self._join ("INNER JOIN", obj, alias, *Qs, **filters)
	
	def left_join	(self, obj, alias, *Qs, **filters):
		return self._join ("LEFT OUTER JOIN", obj, alias, *Qs, **filters)
	
	def right_join	(self, obj, alias, *Qs, **filters):
		return self._join ("RIGHT OUTER JOIN", obj, alias, *Qs, **filters)
	
	def full_join	(self, obj, alias, *Qs, **filters):
		return self._join ("FULL OUTER JOIN", obj, alias, *Qs, **filters)
		
	def as_sql (self):
		data = utils.D (**self._data)
		sql = [
			self._template.format (
				_columns =  data.columns, 
				_values = data.values, 
				_pairs = data.pairs,
				**self._feed
			)
		]
		for join in self._joins:
			sql.append (join)
		_filters = [f for f in self._filters if f]
		_filters and sql.append ("WHERE " + " AND ".join (_filters))
		if self._group_by:
			sql.append (self._group_by)
			self._having and sql.append (self._having)
		self._order_by and sql.append (self._order_by)
		self._limit and sql.append (self._limit)
		self._offset and sql.append (self._offset)
		self._returning and sql.append (self._returning)
		return "\n".join (sql) + ";"
