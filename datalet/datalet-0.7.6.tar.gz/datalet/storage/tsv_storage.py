#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os
import os.path

from datalet.data import *
from datalet.storage.text_file_storage import TextFileStorage
from datalet.storage.exceptions import *

class TsvStorage(TextFileStorage):

	def __init__(self, location):
		super().__init__(location)


	def write(self, data, force = True, overwrite = False, include_header = True, encoding = 'utf-8'):
		"""
		See Storage's notes.
		"""
		if not self.exists():
			if force == True:
				self.create(force = True)
			else:
				raise StorageNotFoundError(self.location)

		openmode = "a" if overwrite == False else "w"
		with open(self.location, openmode, encoding = encoding) as file:
			if write_header == True:
				file.write('\t'.join(data.column_names))
				file.write('\n')
			for row in data:
				file.write('\t'.join(list(map(str, row))))
				file.write('\n')


	def read(self, limit = None, encoding = "utf-8"):
		"""
		See Storage's notes.
		"""
		if not self.exists():
			raise StorageNotFoundError(self.location)

		dt = DataTable()
		with open(self.location, "r", encoding = encoding) as file:
			line_index = 0
			for line in file.readlines():
				if limit is not None and line_index >= limit:
					break
				dt.append(line.rstrip('\n').split('\t'))
				line_index += 1
		return dt
