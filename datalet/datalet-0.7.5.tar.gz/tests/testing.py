#!/usr/bin/env python
# -*- coding: utf-8  -*-

import unittest
import inspect


class Testing(unittest.TestCase):

	def get_func_name(self):
		return inspect.stack()[1][3]