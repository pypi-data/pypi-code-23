#!/usr/bin/env python
# -*- coding: utf-8  -*-

from abc import ABCMeta,abstractmethod

class Validator(object, metaclass = ABCMeta):
	
	@abstractmethod
	def validate(self, columns, datarow):
		pass


class DataTypeValidator(Validator):
	
	def validate(self, columns, datarow):
		pass