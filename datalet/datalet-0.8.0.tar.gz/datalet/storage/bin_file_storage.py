#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os
import os.path
from abc import ABCMeta,abstractmethod

from datalet.storage.file_storage import FileStorage
from datalet.storage.exceptions import *

class BinFileStorage(FileStorage, metaclass = ABCMeta):
	"""
	binary file
	"""

	def __init__(self, location = None):
		super().__init__(location)

	@abstractmethod
	def create(self, force = False):
		pass

	@abstractmethod
	def clear(self, force = False):
		pass

	@abstractmethod
	def write(self, data, force = True, overwrite = False, include_header = True, encoding = 'utf-8'):
		pass

	@abstractmethod
	def read(self, limit = None, encoding = 'utf-8'):
		pass
