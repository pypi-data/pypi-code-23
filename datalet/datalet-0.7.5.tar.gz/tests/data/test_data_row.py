#!/usr/bin/env python
# -*- coding: utf-8  -*-

"""
execute the unittest file in project root directory.
"""
import sys
sys.path.insert(0, r"../datalet")

from datalet.data import *
import unittest
from tests.testing import Testing

class DataRowTesting(Testing):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_integer_index(self):
		pass
