#!/usr/bin/env python
# -*- coding: utf-8  -*-

def flatten(o_dict, pre_fix = None):
	flattened = {}
	for key in o_dict.keys():
		if isinstance(o_dict[key], dict):
			p_flattened = flatten(o_dict[key], pre_fix = key)
			flattened = dict(flattened, ** p_flattened)
		else:
			new_key = key if pre_fix is None else pre_fix + "." + key
			flattened[new_key] = o_dict[key]
	return flattened