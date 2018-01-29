#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os.path

import xlrd
import xlwt

from datalet.data import *
from datalet.storage.bin_file_storage import BinFileStorage
from datalet.storage.exceptions import (StorageExistsError
	, StorageNotFoundError
	, UnmatchExtensionError
	, ArgumentsAbsenceError)


class Excel2003Storage(BinFileStorage):
	"""
	Excel 2003 format Storage
	"""


	def __init__(self, filepath = None, sheetIndex = -1, sheetName = None):
		super().__init__(filepath)
		self.sheetIndex = sheetIndex
		self.sheetName = sheetName


	def __get_worksheet(self, workbook_toread):
		ws = None
		if self.sheetName is not None:
			ws = workbook_toread.sheet_by_name(self.sheetName)
		else:
			if self.sheetIndex is not -1:
				ws = workbook_toread.sheet_by_index(self.sheetIndex)
			else:
				raise ArgumentsAbsenceError("The targetSheet arguments must be specified one:  sheetIndex=%s, sheetName=%s" % \
					(self.sheetIndex, self.sheetName))
		return ws


	def create(self, force = False):
		if self.exists():
			if force == False:
				raise StorageExistsError(self.filepath)
			else:
				self.remove(force = True)

		wb_w = xlwt.Workbook(encoding='utf-8', style_compression=0)
		createSheetName = self.sheetName if self.sheetName is not None else ("SHEET_" + str(self.sheetIndex))
		sheet = wb_w.add_sheet(createSheetName, cell_overwrite_ok = True)
		wb_w.save(self.filepath)


	def clear(self, force = False):
		if not self.exists():
			if force == False:
				raise StorageNotFoundError(self.filepath)

		raise NotImplementedError()


	def read(self, limit =  -1):
		dt = DataTable()
		wb = xlrd.open_workbook(self.filepath)
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
