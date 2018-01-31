#!/usr/bin/env python
# -*- coding: utf-8  -*-

import inspect

def get_current_func_name():
	return inspect.stack()[1][3]
