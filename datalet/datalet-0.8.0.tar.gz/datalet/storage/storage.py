#!/usr/bin/env python
# -*- coding: utf-8  -*-

from abc import ABCMeta,abstractmethod

class Storage(object, metaclass = ABCMeta):

	def __init__(self, location):
		"""Init an storage.

		Args:
			location:
				When the storage is a file, the location is filepath;
				When the storage is a database, the location is sqlalchemy url.
		"""
		self.__location = location

	@property
	def location(self):
		return self.__location

	@location.setter
	def location(self, val):
		self.__location = val

	@abstractmethod
	def exists(self):
		"""Return True if the storage is existing, otherwise return False.

		Returns:
			Boolean
		"""
		pass

	@abstractmethod
	def create(self, force = True):
		"""Create a storage.

		Args:
			force:
				The storage will remove the old one and create a new one if force is True when the storage is existed otherwise raise a StorageExistedError.

		Returns:
			None

		Raises:

		"""
		pass

	@abstractmethod
	def clear(self, force = False):
		"""Clear the conent of storage.

		Args:
			force:
				The storage will be cleared cascadely if force is True when the storage has foreign relations, otherwise raise a ForeignRelationExistedError;
			 	The storage will do nothing if force is True when the storage is not existed otherwise raise a StorageNotFoundError.

		Returns:
			None
		"""
		pass

	@abstractmethod
	def remove(self, force = False):
		"""Remove the storage.

		Args:
			force:
				The storage will be removed cascadely if force is True when the storage has foreign relations, otherwise raise a ForeignRelationExistedError;
				The storage will do nothing if force is True when the storage is not existed otherwise raise a StorageNotFoundError.

		Returns:
			None
		"""
		pass

	@abstractmethod
	def write(self, data, force = True, overwrite = False, include_header = True, encoding = 'utf-8'):
		"""Write data to the storage.

		Args:
			data:
				The data to write. The data's type is DataTable(datalet.data.DataTable).
			force:
				The storage will be created if force is True when the storage is not existed otherwise raise a StorageNotFoundError.
			overwrite:
				Whether overwrite the existing data.
			include_header:
				Whether include the header if the data has header.

		Returns:
			None
		"""
		pass

	@abstractmethod
	def read(self, limit = None, encoding = 'utf-8'):
		"""Read data from the storage.

		Args:
			limit:
				Read all rows if limit is None, otherwise read the limit rows data.

		Returns:
			DataTable(datalet.data.DataTable)
		"""
		pass

	@abstractmethod
	def copy(self, copy_to_path = None):
		"""Copy the storage.

		Args:
			copy_to_path:
				The path to copy.

		Returns:
			None
		"""
		pass
