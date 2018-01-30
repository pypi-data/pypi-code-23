#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os.path
import math

from sqlalchemy import create_engine, text, select, exists
from sqlalchemy.schema import CreateSchema

from datalet.storage.storage import Storage
from datalet.storage.db_types import DataBaseTypes
from datalet.storage.exceptions import *

class DbTableStorage(Storage):

	def __init__(self, dburl, table, engine_echo = False):
		location = {"dburl": dburl, "table": table}
		super().__init__(location)
		self.dburl = dburl
		self.table = table
		self.engine = create_engine(self.dburl, echo = engine_echo)
		self.table.metadata.bind = self.engine

	def get_engine(self):
		return self.engine

	def get_table(self):
		return self.table

	def __exists_schema(self, schema_name):
		txt_exists_schema = text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema_name")
		schemanames = self.engine.execute(txt_exists_schema, schema_name = schema_name).fetchall()
		return len(schemanames) > 0


	def create(self, force = False, partition_by = None):
		if self.exists():
			if force == True:
				self.remove(force = True)
			else:
				raise StorageExistedError(self.location)
		# create
		if not self.__exists_schema(self.table.schema):
			self.engine.execute(CreateSchema(self.table.schema))
		return self.table.create()


	def exists(self):
		return self.table.exists()


	def clear(self, force = False):
		if not self.exists():
			if force == False:
				raise StorageNotFoundError(self.location)
		return self.table.delete()


	def remove(self, force = False):
		if not self.exists():
			if force == False:
				raise StorageNotFoundError(self.location)
		else:
			self.table.drop()


	def copy(self, path = None):
		pass


	def read(self, limit =  -1):
		return self.engine.execute(self.table.select())


	def write(self, data, overwrite = False, batch_rows_count = -1):
		"""
		DataFrame.to_dict(orient = "records")
		"""
		if not self.exists():
			raise StorageNotFoundError(self.location)

		if not isinstance(data, list):
			data = list(data)

		# TODO: make it to support generator.
		if overwrite == True:
			self.clear(force = True)

		if batch_rows_count <= 0:
			return self.engine.execute(self.table.insert(), data)
		else:
			rows_count = len(data)
			batch_count = 1 if batch_rows_count >= rows_count else math.ceil(rows_count / batch_rows_count)
			# start transaction ??
			with self.engine.begin() as conn:
				trans = conn.begin()
				try:
					for batch_index in range(0, batch_count):
						start_index = batch_index * batch_rows_count
						end_index = rows_count if batch_index == (batch_count - 1) else start_index + batch_rows_count
						print("proc>>> batch index: %d, start index: %d, end index: %d" % (batch_index, start_index, end_index))

						conn.execute(self.table.insert(), data[start_index: end_index])
					trans.commit()
				except:
					trans.rollback()
					raise
			return (rows_count, batch_count)
