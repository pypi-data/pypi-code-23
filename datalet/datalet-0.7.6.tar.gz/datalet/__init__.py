#!/usr/bin/env python
# -*- coding: utf-8  -*-


from datalet.storage import Storage, FileStorage, \
	TextFileStorage, BinFileStorage, \
	CsvStorage, TsvStorage, \
	ExcelStorage, ExcelXlsStorage, ExcelXlsxStorage, \
	EmlStorage, HtmlStorage



__version__ = '0.7.6'

def create_storage(location, type, **kwargs):
	if kwargs is None or len(kwargs) == 0:
		kwargs = {}
