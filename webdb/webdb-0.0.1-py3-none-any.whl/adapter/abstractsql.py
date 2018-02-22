from abc import abstractmethod
from .abc import AbstractDB
from .exceptions import NotSupportedError, DatabaseError
from ..typehandling.typehandling import handle_types

class AbstractSQLDB(AbstractDB):
	"""
	An abstract SQL DB adapter. The following methods must be overwritten:
	``open``, ``close``, ``get_column_names``, ``get_table_names``.

	"""
	def __init__(self):
		self._con = None
		self.handlers = {"INSERT": self.handle_insert,
			"UPDATE": self.handle_update,
			"DELETE": self.handle_delete,
			"SELECT": self.handle_select}

	@abstractmethod
	def get_column_names(self, table):
		"""
		Return a list with the column names in this table.
		"""
		pass
	@abstractmethod
	def get_table_names(self):
		"""
		Return a list of table names in this database.
		"""
		pass
	
	def handle_request(self, request, inject = None, inject_as = None):
		if(not request["operation"] in self.handlers):
			raise NotSupportedError(request["operation"])

		table_names = self.get_table_names()
		if(not request["table"] in table_names):
			raise DatabaseError("unknown table: {}".format(request["table"]))

		return self.handlers[request["operation"]](request, inject, inject_as)

	def handle_insert(self, request, inject, inject_as):
		if(inject_as):
			request["parameters"][inject_as] = inject

		data = handle_types(request["parameters"])

		column_names = self.get_column_names(request["table"])
		for cname in data:
			if(not cname in column_names):
				raise DatabaseError("unknown column: {}".format(cname))

		columns, values = zip(*data.items())
		sql_columns = ",".join(columns)
		sql_values = ",".join(["?"] * len(values))
		sql_string = "INSERT INTO {}({}) VALUES({})".format(
				request["table"],
				sql_columns,
				sql_values)
		cursor = self._con.cursor()
		cursor.execute(sql_string, values)
		self._con.commit()

	def handle_update(self, request, inject, inject_as):
		where = request["parameters"]["where"]
		set_to = request["parameters"]["set"]

		if(inject_as):
			where[inject_as] = inject
			set_to[inject_as] = inject
		
		column_names = self.get_column_names(request["table"])
		
		for cname in set_to:
			if(not cname in column_names):
				raise DatabaseError("unknown column: {}".format(cname))
		for cname in where:
			if(not cname in column_names):
				raise DatabaseError("unknown column: {}".format(cname))

		where = handle_types(where)
		set_to = handle_types(set_to)

		where_columns, where_values = zip(*where.items())
		set_to_columns, set_to_values = zip(*set_to.items())

		where_sql = " AND ".join(["{}=?".format(col) for col in where_columns]) 
		set_sql = ",".join(["{}=?".format(col) for col in set_to_columns])

		sql_string = "UPDATE {} SET {} WHERE {}".format(request["table"], set_sql, where_sql)

		cursor = self._con.cursor()
		cursor.execute(sql_string, set_to_values + where_values)
		self._con.commit()


	def handle_select(self, request, inject, inject_as):
		what = request["parameters"]["what"]
		where = request["parameters"]["where"]

		if(inject_as):
			where[inject_as] = inject
		
		column_names = self.get_column_names(request["table"])
		
		for cname in what:
			if(not cname in column_names):
				raise DatabaseError("unknown column: {}".format(cname))
		for cname in where:
			if(not cname in column_names):
				raise DatabaseError("unknown column: {}".format(cname))

		where = handle_types(where)
		if(where):
			where_columns, where_values = zip(*where.items())

			where_sql = " AND ".join(["{}=?".format(col) for col in where_columns])
		else:
			where_columns, where_values = [], []

		what_sql = ",".join(what)

		sql_string = "SELECT "
		if(what):
			sql_string += what_sql + " "
		else:
			sql_string += "* "

		sql_string += "FROM {} ".format(request["table"])

		if(where):
			sql_string += "WHERE {}".format(where_sql)


		cursor = self._con.cursor()
		cursor.execute(sql_string, where_values)

		return cursor.fetchall()

	def handle_delete(self, request, inject, inject_as):
		where = request["parameters"]
		if(inject_as):
			where[inject_as] = inject

		column_names = self.get_column_names(request["table"])
		
		for cname in where:
			if(not cname in column_names):
				raise DatabaseError("unknown column: {}".format(cname))

		where = handle_types(where)
		where_columns, where_values = zip(*where.items())

		where_sql = " AND ".join(["{}=?".format(col) for col in where_columns])

		sql_string = "DELETE FROM {} WHERE {}".format(request["table"], what_sql)

		cursor = self._con.cursor()
		cursor.execute(sql_string, set_to_values + where_values)
		self._con.commit()
