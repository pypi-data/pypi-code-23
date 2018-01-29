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

	def __init__(self, filepath = None):
		super().__init__(filepath)
		self.filepath = self.location


	def create(self, force = False):
		# if the file existed
		if self.exists():
			if force == False:
				raise StorageExistsError(self.filepath)
			else:
				self.remove(force = True)

		(head, tail) = os.path.split(self.filepath)
		if head != "" and (not os.path.exists(head)):
			os.makedirs(head)
		with open(self.filepath, "w") as file:
			pass


	def clear(self, force = False):
		if not self.exists():
			if force == False:
				raise StorageNotFoundError(self.filepath)
		with open(self.filepath, "w", encoding="utf-8") as file:
			file.truncate()


	@abstractmethod
	def write(self, data, overwrite = False):
		pass

	@abstractmethod
	def read(self, limit = -1, encoding = "utf-8"):
		pass
