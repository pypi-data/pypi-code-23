#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os
import os.path

from datalet.data import *
from datalet.storage.text_file_storage import TextFileStorage
from datalet.storage.exceptions import (StorageExistsError
	, StorageNotFoundError)

class TsvStorage(TextFileStorage):

	def __init__(self, filepath):
		super().__init__(filepath)


	def write(self, data, overwrite = False, encoding = "utf-8", write_header = True):
		if not self.exists():
			raise StorageNotFoundError(self.filepath)
		openmode = "a" if overwrite == False else "w"
		with open(self.filepath, openmode, encoding = encoding) as file:
			if write_header == True:
				file.write('\t'.join(data.column_names))
				file.write('\n')
			for row in data:
				file.write('\t'.join(list(map(str, row))))
				file.write('\n')


	def read(self, limit = -1, encoding = "utf-8"):
		if not self.exists():
			raise StorageNotFoundError(self.filepath)
		dt = DataTable()
		with open(self.filepath, "r", encoding = encoding) as file:
			line_index = 0
			for line in file.readlines():
				if limit != -1 and line_index >= limit:
					break
				dt.append(line.rstrip('\n').split('\t'))
				line_index += 1
		return dt
