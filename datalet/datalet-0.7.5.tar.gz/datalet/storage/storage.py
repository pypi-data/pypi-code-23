#!/usr/bin/env python
# -*- coding: utf-8  -*-

from abc import ABCMeta,abstractmethod

class Storage(object, metaclass = ABCMeta):

	def __init__(self, location):
		"""
		When the storage is a file, the location is filepath;
		When the storage is a database, the location is database connection info directory;
		"""
		self.location = location

	@abstractmethod
	def exists(self):
		"""
		Return True if the storage is existing, otherwise return False.
		"""
		pass

	@abstractmethod
	def create(self, force = False):
		"""
		When the storage is not existing, a new storage will be created;
		When the storage is existing and force is False, a StorageExistsError will be raised;
		When the storage is existing and force is True, the old storage will be removed(cascade) firstly and then a new one will be created. 
		"""
		pass

	@abstractmethod
	def clear(self, force = False):
		"""
		When the storage is not existing and force is False, a StorageNotFoundError will be raised;
		When the storage is not existing and force is True, nothing will be done;
		When the storage has no foreign relation, the storage will be cleared directly;
		When the storage has foreign relations and force is False, a ForeignRelationExistsError will be raised;
		When the storage has foreign relations and force is True, the storage will be cleared cascade.
		"""
		pass

	@abstractmethod
	def remove(self, force = False):
		"""
		When the storage is not existing and force is False, a StorageNotFoundError will be raised;
		When the storage is not existing and force is True, nothing will be done;
		When the storage has no foreign relation, the storage will be removed directly;
		When the storage has foreign relations and force is False, a ForeignRelationExistsError will be raised;
		When the storage has foreign relations and force is True, the storage will be removed cascade.
		"""
		pass

	@abstractmethod
	def write(self, data, overwrite = False, write_header = True):
		"""
		When the overwrite is False, the data will be appended to the end of the storage;
		When the overwrite is True, the storage will be cleared(cascade) firstly and then the data will be writed to the storage;
		"""
		pass

	@abstractmethod
	def read(self, limit = -1):
		"""
		When the limit equals -1, will return all data in the storage;
		WHen the limit is specified a limit number, will return the limit number rows data.
		"""
		pass

	@abstractmethod
	def copy(self, path = None):
		"""
		When name is None, the default name is ( oldname + "_copy" );
		When name is not None, use the specified name.
		"""
		pass
