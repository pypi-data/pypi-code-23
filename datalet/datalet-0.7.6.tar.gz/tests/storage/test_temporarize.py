"""
execute the unittest file in project root directory.
"""
import sys
sys.path.insert(0, r"../datalet")

import os
import unittest
import time

from datalet.storage.temporarize import Temporarize
from tests.testing import Testing


class TemporarizeTesting(unittest.TestCase):
	def setUp(self):
		self.tmpdir = r"tests/test_data/tmp/"
		self.classname = self.__class__.__name__
		self.separator = "$"
		self.ext = ".csv"

	def tearDown(self):
		pass

	# def test_used_by_with(self):
	# 	testfile = self.classname + self.separator + self.ext
	# 	testfile_fullpath = self.tmpdir + testfile
	# 	with Temporarize(location = testfile_fullpath) as tmp:
	# 		if tmp is not None:
	# 			self.assertTrue(tmp.exists())
	# 			time.sleep(5)

	def test_used_not_by_with(self):
		pass


def suite():
	suite = unittest.TestSuite()
	suite.addTest(TemporarizeTesting("test_used_by_with"))
	suite.addTest(TemporarizeTesting("test_used_not_by_with"))
	return suite

if __name__ == "__main__":
	unittest.main(defaultTest = "suite")
