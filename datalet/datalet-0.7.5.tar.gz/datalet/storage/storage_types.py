#!/usr/bin/env python
# -*- coding: utf-8  -*-

from enum import Enum, IntEnum, unique

@unique
class StorageTypes(IntEnum):
	CSV = 10101
	HTML = 10102
	HTM = 10103
	EML = 10104
	TSV = 10105
	XLS = 10201
	XLSX = 10202
	DATABASE = 10301