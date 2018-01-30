#!/usr/bin/env python
# -*- coding: utf-8  -*-

import json

from datalet.data.data_column import DataColumn
from datalet.data.data_row import DataRow
from datalet.data.exceptions import *

class DataTable(object):
	"""
	DataTable is read schema.
	It can stores the data in any format, but use the schema validating on read.

	EXAMPLE:

	Create DataTable:
		# create from list of list
		dt = DataTable(name = 'abc', columns = [], rows = [])

	Get Rows:
		# get first row
		dt[0]

		# get 1-5 rows
		dt[1: 6]

	Iterate Rows:
		for row in dt:
			...

	Get Columns:
		col_names = dt.column_names

	Get Columns Data:
		col_name_data = dt["name"]

	Get Cell Data:
		dt[row_index][col_name]
		dt[row_index].col_name
	"""

	def __init__(self, name = None, columns = [], rows = []):
		"""

		"""
		self.__name = name
		self.__rows = []
		self.__columns = []

		columns = list(columns)
		for col in columns:
			if isinstance(col, DataColumn):
				self.__columns.append(col)
			elif isinstance(col, str):
				self.__columns.append(DataColumn(col))
			else:
				raise ArgumentTypeError(columns)
		rows = list(rows)

		for row in rows:
			self.append(row)

	def __getitem__(self, key):
		"""
		if key is int or slice, get rows.
		if key is str, get column data.
		"""
		if isinstance(key, int) or isinstance(key, slice):
			return self.__rows[key]
		elif isinstance(key, str):
			return (row[key] for row in self.__rows)
		else:
			raise ArgumentTypeError(datarow, ["str", "int", "slice"])

	def __setitem__(self, key, value):
		self.__rows[key] = value

	def __delitem__(self, key):
		del self.__rows[key]

	def __iter__(self):
		return iter(self.__rows)

	def __len__(self):
		return len(self.__rows)

	def __str__(self):
		return json.dumps(self.__dict__)

	@property
	def name(self):
		return self.__name

	@name.setter
	def name(self, value):
		self.__name = value

	@property
	def columns(self):
		return self.__columns

	@columns.setter
	def columns(self, value):
		self.__columns = value

	@property
	def column_names(self):
		return [col.name for col in self.__columns]

	@property
	def shape(self):
		return (len(self.__rows), len(self.__columns))

	@property
	def rows_count(self):
		return len(self.__rows)


	def get_column_index(self, column):
		'''
		Get the index of column in the table.
		'''
		if isinstance(column, str):
			return self.column_names.index(column)
		elif isinstance(column, DataColumn):
			return self.__columns.index(column)
		else:
			raise ArgumentTypeError(datarow, ["str", "DataColumn"])


	def append(self, datarow, append_columns = False):
		'''
		Append row to table.
		'''
		if isinstance(datarow, DataRow):
			datarow.owner_table = self
			self.__rows.append(datarow)
		elif isinstance(datarow, list) or isinstance(datarow, tuple):
			self.__rows.append(DataRow(self, datarow))
		elif isinstance(datarow, dict):
			if self.__columns is None:
				raise RequiredFieldNoneError("columns")
			row_data = []
			for column in self.__columns:
				row_data.append(datarow.get(column.name, None))
			self.__rows.append(DataRow(self, row_data))
		else:
			raise ArgumentTypeError(datarow, ["list", "DataRow", "dict"])
		return self

	def extend(self, dt):
		'''
		Extend current table by appending all rows of another table.
		'''
		if isinstance(dt, DataTable):
			self.__rows.extend([row for row in dt])
		else:
			raise ArgumentTypeError(dt, "DataTable")
		return self

	def validate(self, *validators):
		pass

	def shift_rows_to_header(self, rows_count):
		if rows_count <= 0:
			raise OutOfRangeError("rows_count")

		header_rows = [self.__rows.pop(row_index) for row_index in range(0, rows_count)]
		zipped_headers = zip(*header_rows)
		column_names = ['&'.join(list(ziped_col_names)) for ziped_col_names in zipped_headers]
		self.__columns = [DataColumn(colname) for colname in column_names]

	def clear(self):
		''' clear the data in datatable, but not affect the columns.
		'''
		self.__rows = []


	def to_dict(self, key_field = "name", null_expr = None):
		'''
		return generator
		'''
		return (row.to_dict(key_field, null_expr) for row in self.__rows)


	def to_list(self):
		'''
		return generator
		'''
		return (row.to_list() for row in self.__rows)


	def to_pandas_dataframe(self, column_field = "name"):
		import pandas as pd
		column_names = [col[column_field] for col in self.__columns]
		return pd.DataFrame(data = list(self.to_list()), columns = column_names)

	def to_spark_dataframe(self):
		pass

	def to_spark_rdd(self):
		pass

	def from_pandas_dataframe(self, dataframe, null_expr = None):
		import pandas as pd
		if not isinstance(dataframe, pd.DataFrame):
			raise ArgumentTypeError(dataframe, type(pd.DataFrame))
		self.__columns = [DataColumn(column) for column in dataframe.columns]
		self.__rows = [DataRow(self, [null_expr if pd.isnull(d) else d for d in row]) \
				 for row in dataframe.values]

	@staticmethod
	def from_list(src_list, null_expr = None):
		"""
		Parse DataTable from list. The first element of the source list will be as the header columns.

		Args:
			src_list:
				The source list.

		Returns:
			DataTable
		"""

		columns = [DataColumn(column) for column in src_list[0]]
		rows = [DataRow(data = row) for row in src_list[1:]]
		return DataTable(name = None, columns = columns, rows = rows)
