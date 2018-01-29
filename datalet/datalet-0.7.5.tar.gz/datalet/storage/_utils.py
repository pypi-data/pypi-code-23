#!/usr/bin/env python
# -*- coding: utf-8  -*-

from inspect import signature

from actlet.storage.excel_storage import ExcelStorage
from actlet.storage.csv_storage import CsvStorage
from actlet.storage.tsv_storage import TsvStorage
from actlet.storage.eml_storage import EmlStorage
from actlet.storage.html_storage import HtmlStorage
from actlet.storage.dbtable_storage import DbTableStorage
from actlet.storage.storage_types import StorageTypes
from actlet.storage.exceptions import *

__ext_2_storage_func = {StorageTypes.XLS: ExcelStorage, 
				 StorageTypes.XLSX: ExcelStorage, 
				 StorageTypes.CSV: CsvStorage, 
				 StorageTypes.TSV: TsvStorage,
				 StorageTypes.HTML: HtmlStorage, 
				 StorageTypes.HTM: HtmlStorage,
				 StorageTypes.EML: EmlStorage}


def get_storage_func(filepath = None, type = None):
	"""
	Get storage's construct function.
	"""
	if type is not None:
		if isinstance(type, StorageTypes):
			return __ext_2_storage_func[type]
		elif isinstance(type, str):
			return __ext_2_storage_func[StorageTypes[type.upper()]]
		else:
			raise TypeError("type")
	else:
		ext = filepath.split(".")[-1].upper()
		if StorageTypes[ext] in __ext_2_storage_func:
			return __ext_2_storage_func[StorageTypes[ext]]
		else:
			raise UnmatchExtensionError(filepath)


def call_func(func, args):
	"""
	Only pass the arguments whoes name is existed in function's paramsters.
	"""
	sig = signature(func)
	to_pass_args = {}
	for param in sig.parameters.values():
		if param.name in args:
			to_pass_args[param.name] = args[param.name]
	return func(**to_pass_args)

