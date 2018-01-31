#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os.path

from datalet.storage.bin_file_storage import BinFileStorage
from datalet.storage.excel_xls_storage import ExcelXlsStorage
from datalet.storage.excel_xlsx_storage import ExcelXlsxStorage
from datalet.storage.exceptions import *


class ExcelStorage(BinFileStorage):

	def __init__(self, location = None, sheet_index = None, sheet_name = None):
		super().__init__(location)

		ext = self.location.split(".")[-1].upper()
		if ext == "XLS":
			self.excel_storage = ExcelXlsStorage(location = location, sheet_index = sheet_index, sheet_name = sheet_name)
		elif ext == "XLSX":
			self.excel_storage = ExcelXlsxStorage(location = location, sheet_index = sheet_index, sheet_name = sheet_name)
		else:
			raise UnmatchExtensionError(ext)


	def create(self, force = False):
		return self.excel_storage.create(force = force)


	def clear(self, force = False):
		return self.excel_storage.clear(force = force)


	def write(self, data, force = True, overwrite = False, include_header = True, encoding = 'utf-8'):
		return self.excel_storage.write(data = data, force = force, overwrite = overwrite, include_header = include_header, encoding = encoding)


	def read(self, limit = None, encoding = 'utf-8'):
		return self.excel_storage.read(limit = limit, encoding = encoding)
