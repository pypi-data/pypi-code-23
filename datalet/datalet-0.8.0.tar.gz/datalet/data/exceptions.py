#!/usr/bin/env python
# -*- coding: utf-8  -*-

class ArgumentTypeError(Exception):

	def __init__(self, arg_value, param_type):
		self.arg_value = arg_value
		self.param_type = param_type

class ItemNotFoundError(Exception):

	def __init__(self, item):
		self.item = item

class AttributeNotFoundError(Exception):

	def __init__(self, attr_name):
		self.attr_name = attr_name

class RequiredFieldNoneError(Exception):

	def __init__(self, filed_name):
		self.field_name = field_name

class OutOfRangeError(Exception):

	def __init__(self, field_name):
		self.field_name = field_name
