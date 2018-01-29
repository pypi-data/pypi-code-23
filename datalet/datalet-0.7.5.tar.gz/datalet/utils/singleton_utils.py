#!/usr/bin/env python
# -*- coding: utf-8  -*-

def singleton(cls, *args, **kw):
	instances = {}
	def __singleton():
		if cls not in instances:
			instances[cls] = cls(*args, **kw)
		return instances[cls]
	return __singleton