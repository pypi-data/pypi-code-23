#!/usr/bin/env python
# -*- coding: utf-8  -*-

"""
execute the unittest file in project root directory.
"""
import sys
sys.path.insert(0, r"../datalet")

import unittest

from datalet.storage import *
from tests.testing import Testing


class BinFileStorageTest(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_instance(self):
		with self.assertRaises(TypeError):
			s = BinFileStorage() # can not instance

def suite():
	suite = unittest.TestSuite()
	suite.addTest(BinFileStorageTest("test_instance"))
	return suite

if __name__ == "__main__":
	unittest.main(defaultTest = "suite")
