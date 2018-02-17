from . import sql

class Operation:
	def __init__ (self, engine = 'postresql'):
		self.engine = engine
		
	def insert (self, table, **fields):
		q = sql.SQLComposer ("INSERT INTO " + table + " ({_columns}) VALUES ({_values})", self.engine)
		q.data (**fields)
		return q
	
	def update (self, table, **fields):		
		q = sql.SQLComposer ("UPDATE " + table + " SET {_pairs}", self.engine)
		q.data (**fields)
		return q
	
	def select (self, table, *select):
		q = sql.SQLComposer ("SELECT {select} FROM " + table, self.engine)
		q.columns (*select)
		return q
	
	def delete (self, table):
		q = sql.SQLComposer ("DELETE FROM " + table, self.engine)
		return q

