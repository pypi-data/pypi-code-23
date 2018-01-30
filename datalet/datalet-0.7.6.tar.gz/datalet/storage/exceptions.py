#!/usr/bin/env python
# -*- coding: utf-8  -*-

class StorageExistedError(Exception):

	def __init__(self, location):
		self.location = location

class StorageNotFoundError(Exception):

	def __init__(self, location):
		self.location = location

class UnmatchExtensionError(Exception):

	def __init__(self, extname):
		self.extname = extname

class ForeignRelationExistedError(Exception):

	def __init__(self, location):
		self.location = location

class ArgumentsAbsenceError(Exception):

	def __init__(self, argname):
		self.argname = argname

class ArgumentsTypeError(Exception):

	def __init__(self, argname):
		self.argname = argname
