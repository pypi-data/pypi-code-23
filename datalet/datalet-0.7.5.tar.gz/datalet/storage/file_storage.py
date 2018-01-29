#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os
import os.path
from abc import ABCMeta,abstractmethod

from datalet.storage.storage import Storage
from datalet.storage.exceptions import *

class FileStorage(Storage, metaclass = ABCMeta):

	POSTFIX = "$COPY"

	def __init__(self, filepath = None):
		super().__init__(filepath)
		self.filepath = self.location


	def exists(self):
		return os.path.exists(self.filepath)


	def remove(self, force = False):
		if not self.exists():
			if force == False:
				raise StorageNotFoundError(self.filepath)
		else:
			os.remove(self.filepath)


	def copy(self, path = None):
		if not self.exists():
			raise StorageNotFoundError(self.filepath)
		import shutil
		if path is not None:
			shutil.copyfile(self.filepath, path)
		else:
			newname = None
			dirname = os.path.dirname(self.filepath)
			filename = os.path.basename(self.filepath)
			sections = filename.split(".")
			newname = sections[0] + FileStorage.POSTFIX + "." + sections[1] if len(sections) == 2 else sections[0] + FileStorage.POSTFIX
			shutil.copyfile(self.filepath, dirname + os.path.sep + newname)

	@abstractmethod
	def create(self, force = False):
		pass

	@abstractmethod
	def clear(self, force = False):
		pass

	@abstractmethod
	def write(self, data, overwrite = False):
		pass

	@abstractmethod
	def read(self, limit = -1):
		pass
