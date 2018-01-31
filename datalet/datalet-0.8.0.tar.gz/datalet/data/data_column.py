#!/usr/bin/env python
# -*- coding: utf-8  -*-

import json

class DataColumn(object):
	
	def __init__(self, name, caption = None, data_type = type(str), nullable = True, default_value = None):
		self.name = name
		self.caption = caption
		self.data_type = data_type
		self.nullable = nullable
		self.default_value = default_value
		
	def __getattr__(self, attr_name):
		return self.__dict__.get(attr_name)

	def __setattr__(self, attr_name, attr_val):
		self.__dict__[attr_name] = attr_val

	def __delattr__(self, attr_name):
		del self.__dict__[attr_name]

	def __getitem__(self, key):
		return self.__getattr__(key)

	def __setitem__(self, key, value):
		self.__setattr__(key, value)

	def __delitem__(self, key):
		self.__delattr__(key)

	def __str__(self):
		return json.dumps(self)
