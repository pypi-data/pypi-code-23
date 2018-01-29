#!/usr/bin/env python
# -*- coding: utf-8  -*-

import datalet.storage._utils as _utils


def exists_file(filepath, storage_type = None, **kwargs):
	if kwargs is None or len(kwargs) == 0:
		kwargs = {}
	kwargs["filepath"] = filepath
	construct_func = _utils.get_storage_func(filepath, storage_type)
	storage_obj = _utils.call_func(construct_func, kwargs)
	return _utils.call_func(storage_obj.exists, kwargs)


def create_file(filepath,  storage_type = None, force = False, **kwargs):
	if kwargs is None or len(kwargs) == 0:
		kwargs = {}
	kwargs["filepath"] = filepath
	kwargs["force"] = force
	construct_func = _utils.get_storage_func(filepath, storage_type)
	storage_obj = _utils.call_func(construct_func, kwargs)
	return _utils.call_func(storage_obj.create, kwargs)


def clear_file(filepath,  storage_type = None, force = False,**kwargs):
	if kwargs is None or len(kwargs) == 0:
		kwargs = {}
	kwargs["filepath"] = filepath
	kwargs["force"] = force
	construct_func = _utils.get_storage_func(filepath, storage_type)
	storage_obj = _utils.call_func(construct_func, kwargs)
	return _utils.call_func(storage_obj.clear, kwargs)


def remove_file(filepath,  storage_type = None, force = False, **kwargs):
	if kwargs is None or len(kwargs) == 0:
		kwargs = {}
	kwargs["filepath"] = filepath
	kwargs["force"] = force
	construct_func = _utils.get_storage_func(filepath, storage_type)
	storage_obj = _utils.call_func(construct_func, kwargs)
	return _utils.call_func(storage_obj.remove, kwargs)


def read_file(filepath, line_limit = -1, storage_type = None, **kwargs):
	if kwargs is None or len(kwargs) == 0:
		kwargs = {}
	kwargs["filepath"] = filepath
	kwargs["line_limit"] = line_limit
	construct_func = _utils.get_storage_func(filepath, storage_type)
	storage_obj = _utils.call_func(construct_func, kwargs)
	return _utils.call_func(storage_obj.read, kwargs)


def write_file(filepath, storage_type = None, data = None, overwrite = True, **kwargs):
	if kwargs is None or len(kwargs) == 0:
		kwargs = {}
	kwargs["filepath"] = filepath
	kwargs["data"] = data
	kwargs["overwrite"] = overwrite
	construct_func = _utils.get_storage_func(filepath, storage_type)
	storage_obj = _utils.call_func(construct_func, kwargs)
	return _utils.call_func(storage_obj.write, kwargs)


def create_db(filepath,  storage_type = None, force = False, **kwargs):
	raise NotImplementedError


def create_temp_storage(filepath, force = False, **kwargs):
	raise NotImplementedError
