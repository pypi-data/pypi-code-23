#!/usr/bin/env python
# -*- coding: utf-8  -*-

from enum import Enum, IntEnum, unique

@unique
class DataBaseTypes(IntEnum):
	POSTGRESQL = 10101
	MYSQL = 10102
	SQLITE = 10103
	MSSQLSERVER = 10104
	ORACLE = 10105