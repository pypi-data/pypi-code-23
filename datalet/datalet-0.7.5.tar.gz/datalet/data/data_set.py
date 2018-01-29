#!/usr/bin/env python
# -*- coding: utf-8  -*-

import json
from datalet.data.exceptions import *

class DataSet(object):

	def __init__(self):
		self.__tables = [];

	def __getitem__(self, key):
		if isinstance(key, int) or isinstance(key, slice):
			return self.__tables[key]
		elif isinstance(key, str):
			return [table for table in self.__tables if table.name == key]
		else:
			raise ArgumentTypeError(key, type(str))

	def __setitem__(self, key, value):
		if isinstance(key, int) or isinstance(key, slice):
			self.__tables[key] = value
		elif isinstance(key, str):
			if len(self.__getitem__(key)) == 0:
				self.__tables.append(value)
			else:
				for table in self.__tables:
					if table.name == key:
						table = value
		else:
			raise ArgumentTypeError(key, type(str))

	def __delitem__(self, key):
		del self.__tables[key]

	def __len__(self):
		return len(self.__tables)

	def __iter__(self):
		return iter(self.__tables)

	def __contains__(self):
		pass

	def __del__(self):
		del self.__tables

	def __str__(self):
		return json.dumps(self)

	def append(self, table):
		return self.__tables.append(table)

	def insert(self, index, table):
		return self.__tables.insert(index, table)

	@property
	def tables(self):
		return self.__tables

	@property
	def table_names(self):
		return [table.name for table in self.__tables]
