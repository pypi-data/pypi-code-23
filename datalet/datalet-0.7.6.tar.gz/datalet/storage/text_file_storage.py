#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os
import os.path
from abc import ABCMeta,abstractmethod

from datalet.storage.file_storage import FileStorage
from datalet.storage.exceptions import *

class TextFileStorage(FileStorage, metaclass = ABCMeta):
	"""
	text file
	"""

	def __init__(self, location = None):
		super().__init__(location)


	def create(self, force = False):
		"""
		See Storage's notes.
		"""
		if self.exists():
			if force == False:
				raise StorageExistedError(self.location)
			else:
				self.remove(force = True)

		(head, tail) = os.path.split(self.location)
		if head != "" and (not os.path.exists(head)):
			os.makedirs(head)
		with open(self.location, "w", encoding="utf-8") as file:
			pass


	def clear(self, force = False):
		"""
		See Storage's notes.
		"""
		if not self.exists():
			if force == False:
				raise StorageNotFoundError(self.location)
		with open(self.location, "w", encoding="utf-8") as file:
			file.truncate()


	@abstractmethod
	def write(self, data, overwrite = False):
		pass

	@abstractmethod
	def read(self, limit = -1, encoding = "utf-8"):
		pass
