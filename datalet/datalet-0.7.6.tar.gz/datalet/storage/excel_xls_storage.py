#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os.path

import xlrd
import xlwt

from datalet.data import *
from datalet.storage.bin_file_storage import BinFileStorage
from datalet.storage.exceptions import *


class ExcelXlsStorage(BinFileStorage):
	"""
	Excel 2003 format Storage
	"""


	def __init__(self, location = None, sheet_index = -1, sheet_name = None):
		super().__init__(location)
		self.sheet_index = sheet_index
		self.sheet_name = sheet_name


	def create(self, force = False):
		if self.exists():
			if force == False:
				raise StorageExistedError(self.location)
			else:
				self.remove(force = True)

		wb_w = xlwt.Workbook(encoding='utf-8', style_compression=0)
		new_sheet_name = self.sheet_name if self.sheet_name is not None else ("SHEET_" + str(self.sheet_index))
		sheet = wb_w.add_sheet(new_sheet_name, cell_overwrite_ok = True)
		wb_w.save(self.location)


	def clear(self, force = False):
		if not self.exists():
			if force == False:
				raise StorageNotFoundError(self.location)

		raise NotImplementedError()


	def read(self, limit = None, encoding='utf-8'):
		dt = DataTable()
		wb = xlrd.open_workbook(self.location)
		ws = self.__get_worksheet(wb)

		# get cell data
		for rowIndex in range(0, ws.nrows):
			if limit > -1 and (rowIndex + 1) > limit:
				break

			row = ws.row(rowIndex)
			dr = DataRow()
			for colIndex in range(0, ws.ncols):
				cell = row[colIndex]
				cellval = cell.value
				dr.append(cellval)
			dt.append(dr)

		return dt


	def write(self, data, overwrite = False):
		raise NotImplementedError()

	def __get_worksheet(self, workbook_toread):
		ws = None
		if self.sheet_name is not None:
			ws = workbook_toread.sheet_by_name(self.sheet_name)
		else:
			if self.sheet_index is not -1:
				ws = workbook_toread.sheet_by_index(self.sheet_index)
			else:
				raise ArgumentsAbsenceError("The targetSheet arguments must be specified one:  sheetIndex=%s, sheetName=%s" % \
					(self.sheet_index, self.sheet_name))
		return ws
