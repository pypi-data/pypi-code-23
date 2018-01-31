#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os
import os.path
from abc import ABCMeta,abstractmethod

from datalet.storage.storage import Storage
from datalet.storage.exceptions import *

class FileStorage(Storage, metaclass = ABCMeta):

	def __init__(self, location = None):
		"""Init FileStorage

		Args:
			location: the location is location.
		"""
		super().__init__(location)


	def exists(self):
		"""
		See Storage's notes.
		"""
		return os.path.exists(self.location)


	def remove(self, force = False):
		"""
		See Storage's notes.
		"""
		if not self.exists():
			if force == False:
				raise StorageNotFoundError(self.location)
			else:
				# do nothing.
				pass
		else:
			os.remove(self.location)


	def copy(self, copy_to_path = None):
		"""
		See Storage's notes.
		"""
		if not self.exists():
			raise StorageNotFoundError(self.location)
		if copy_to_path is None:
			raise ArgumentAbsenceError('copy_to_path')

		import shutil
		shutil.copyfile(self.location, copy_to_path)


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
