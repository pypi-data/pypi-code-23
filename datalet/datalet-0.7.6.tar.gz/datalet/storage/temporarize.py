#!/usr/bin/env python
# -*- coding: utf-8  -*-

from datalet.storage.storage import Storage
from datalet.storage.exceptions import *
from datalet.storage._utils import *


class Temporarize(object):
	"""
	usage:
		with Temporarize("location") as temp:
			....
	"""


	def __init__(self, storage = None, location = None, **kwargs):
		self.storage = None
		if storage is not None :
			if isinstance(storage, Storage):
				self.storage = storage
			else:
				raise TypeError(storage)
		else:
			if location is not None:
				if kwargs is None or len(kwargs) == 0:
					kwargs = {}
				kwargs["location"] = location
				kwargs["force"] = True
				if isinstance(location, str):
					construct_func = get_storage_func(location)
					self.storage = call_func(construct_func, kwargs)
					call_func(self.storage.create, kwargs)
				elif isinstance(location, dict):
					#self.storage = sfd.create_db(
					raise NotImplementedError()
			else:
				raise ArgumentsAbsenceError("storage and location must be specified one.")

	def __enter__(self):
		return self.storage

	def __exit__(self, e_t, e_v, t_b):
		if self.storage is not None:
			self.storage.remove(force = True)
