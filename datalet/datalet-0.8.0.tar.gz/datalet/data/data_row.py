#!/usr/bin/env python
# -*- coding: utf-8  -*-

import json

from datalet.data.exceptions import *

class DataRow(object):

	def __init__(self, owner_table = None, data = []):
		"""
		data can be a list

		Args:
			owner_table:
				Parent table. Default is None.
			data:
				Row's data. Default is empty list.
		"""
		self.__owner_table = owner_table
		self.__data = list(data) if data is not None else []

	@property
	def owner_table(self):
		return self.__owner_table

	@owner_table.setter
	def owner_table(self, value):
		self.__owner_table = value

	#def __getattr__(self, key):
	#	pass

		#attr_val = None
		#print(self.__dict__.get("__owner_table"))
		#columns = self.__owner_table.columns
		#columnnames = [col.name for col in self.__owner_table.__columns]
		#if key in columnnames:
		#	idx = columnnames.index(key)
		#	attr_val = self.__data[idx]
		#else:
		#	raise AttributeNotFoundError(key)
		#return attr_val

	#def __setattr__(self, key, value):
	#	pass

	#def __delattr__(self, key):
	#	pass

	def __iter__(self):
		return iter(self.__data)

	def __getitem__(self, key):
		if isinstance(key, str):
			column_index = self.__owner_table.get_column_index(key)
			return self.__data[column_index]
		elif isinstance(key, int) or isinstance(key, slice):
			return self.__data[key]
		else:
			raise ArgumentTypeError(key, "must be str or int or slice type")


	def __setitem__(self, key, value):
		self.__data[key] = value

	def __delitem__(self, key):
		del self.__data[key]

	def __len__(self):
		return len(self.__data)

	def __str__(self):
		return "[" + ",".join(map(str, self.__data)) + "]"

	def append(self, value):
		self.__data.append(value)

	def to_dict(self, dict_key_field = 'name', null_expr = None):
		"""Convert DataRow to a dict.

		Args:
			dict_key_field:
				The field of DataColumn which will be used as dict key expression.
			null_expr:
				The expression that refers null.

		Returns:
			dict
		"""
		if self.__owner_table is None:
			raise RequiredFieldNoneError("owner_table")
		if self.__owner_table.columns is None:
			raise RequiredFieldNoneError("owner_table.columns")

		row_dict = {}
		for i in range(0, len(self.__owner_table.columns)):
			col = self.__owner_table.columns[i]
			dat = self.__data[i]
			row_dict[col[dict_key_field]] = null_expr if dat is None or str(dat).strip() == '' else dat

		return row_dict


	def to_list(self):
		return self.__data
