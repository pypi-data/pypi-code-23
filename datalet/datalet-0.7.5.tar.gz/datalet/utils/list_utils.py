#!/usr/bin/env python
# -*- coding: utf-8  -*-

def split_by_group_count(lst, group_count):
	'''按组个数，尽可能平均分配列表中的元素到各个组中。
	'''
	import math

	groups = []
	sorted_list = sorted(lst)
	list_size = len(sorted_list)
	if group_count >= list_size:
		groups.append(lst)
	else:
		group_size = int(list_size / group_count)
		for group_index in range(0, group_count):
			start_index = group_size * group_index
			end_index = group_size * (group_index + 1)
			end_index = list_size if group_index == (group_count - 1) else end_index
			group = sorted_list[start_index: end_index]
			groups.append(group)
	return groups

def split_by_group_size(lst, group_size):
	'''按组大小，将列表分成多个组。
	'''

	import math

	groups = []
	sorted_list = sorted(lst)
	list_size = len(sorted_list)
	if group_size >= list_size:
		groups.append(lst)
	else:
		group_count = math.ceil(list_size / group_size)
		for group_index in range(0, group_count):
			start_index = group_size * group_index
			end_index = group_size * (group_index + 1)
			end_index = list_size if group_index == (group_count - 1) else end_index
			group = sorted_list[start_index: end_index]
			groups.append(group)
	return groups