"""
execute the unittest file in project root directory.
"""
import sys
sys.path.insert(0, r"../datalet")

import os
import unittest

from datalet.storage import *
from tests.testing import Testing

class EmlStorageTest(unittest.TestCase):

	def setUp(self):
		self.tmpdir = r"tests/test_data/tmp/"
		self.classname = self.__class__.__name__
		self.separator = "$"
		self.ext = ".eml"

	def tearDown(self):
		pass

	# def test_read(self):
	# 	s = EmlStorage(r"tests/test_data/test.eml")
	# 	dat = s.read()
	# 	print(dat)
	# 	self.assertTrue(len(dat) > 0)

def suite():
	suite = unittest.TestSuite()
	#suite.addTest(EmlStorageTest("test_create_file_not_exists"))
	#suite.addTest(EmlStorageTest("test_create_file_exists"))
	#suite.addTest(EmlStorageTest("test_create_file_exists_force"))
	suite.addTest(EmlStorageTest("test_read"))
	#suite.addTest(EmlStorageTest("test_read_limit"))
	#suite.addTest(EmlStorageTest("test_write_append"))
	#suite.addTest(EmlStorageTest("test_write_overwrite"))
	#suite.addTest(EmlStorageTest("test_copy"))
	#suite.addTest(EmlStorageTest("test_copy_path"))
	return suite

if __name__ == "__main__":
	unittest.main(defaultTest = "suite")
