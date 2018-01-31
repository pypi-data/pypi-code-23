#!/usr/bin/env python
# -*- coding: utf-8  -*-

"""
execute the unittest file in project root directory.
"""
import sys
sys.path.insert(0, r"../datalet")

import os
import unittest

from datalet.storage import *
from tests.testing import Testing
from datalet.data import *

class ExcelXlsxStorageTest(unittest.TestCase):

	def setUp(self):
		self.tmpdir = r"tests/test_data/tmp/"
		self.classname = self.__class__.__name__
		self.separator = "$"
		self.ext = ".xlsx"

	def tearDown(self):
		pass

	# def test_create_file_not_exists(self):
	# 	testfile = self.classname + self.separator + self.get_func_name() + self.ext
	# 	s = Excel2007Storage(self.tmpdir + testfile, sheetIndex = 0)
	# 	s.remove(force = True)
	# 	s.create()
	# 	s.remove(force = True)
    #
	# def test_create_file_exists(self):
	# 	testfile = self.classname + self.separator + self.get_func_name() + self.ext
	# 	s = Excel2007Storage(self.tmpdir + testfile, sheetIndex = 0)
	# 	s.remove(force = True)
	# 	s.create()
	# 	with self.assertRaises(StorageExistsError):
	# 		s.create()
	# 	s.remove(force = True)
    #
    #
	# def test_create_file_exists_force(self):
	# 	testfile = self.classname + self.separator + self.get_func_name() + self.ext
	# 	s = Excel2007Storage(self.tmpdir + testfile, sheetIndex = 0)
	# 	s.remove(force = True)
	# 	s.create()
	# 	s.create(force = True)
	# 	s.remove(force = True)
    #
	# def test_read(self):
	# 	s = Excel2007Storage(r"tests/test_data/test.xlsx", sheetIndex = 0)
	# 	dat = s.read()
	# 	self.assertTrue(len(dat) > 0)
    #
	# def test_read_limit(self):
	# 	s = Excel2007Storage(r"tests/test_data/test.xlsx", sheetIndex = 0)
	# 	dat = s.read(limit = 5)
	# 	self.assertTrue(len(dat) == 5)
    #
	# def test_write_append(self):
	# 	testfile = self.classname + self.separator + self.get_func_name() + self.ext
	# 	s = Excel2007Storage(self.tmpdir + testfile, sheetIndex = 0)
	# 	if not s.exists():
	# 		s.create()
	# 	dat = [["a", "b", "c"],[1, 2, 3]]
	# 	s.write(data = dat)
    #
    #
	# def test_write_overwrite(self):
	# 	testfile = self.classname + self.separator + self.get_func_name() + self.ext
	# 	s = Excel2007Storage(self.tmpdir + testfile, sheetIndex = 0)
	# 	s.remove(force = True)
	# 	s.create()
	# 	dt = DataTable("dt", DataColumn(name = "A"), DataColumn(name = "B"))
	# 	dt.append({"A": 111111111111111111111111111111111111111,
	# 		 "B": 22222222222222222222222222222222222})
	# 	# dat = [["a", "b", "c"],[1111111111111111111111111111111, 222222222222222222222222222222222, 3]]
	# 	s.write(data = dt, overwrite = True)
    #
	# def test_copy(self):
	# 	testfile = self.classname + self.separator + self.get_func_name() + self.ext
	# 	s = Excel2007Storage(self.tmpdir + testfile, sheetIndex = 0)
	# 	s.remove(force = True)
	# 	s.create()
	# 	dat = [["a1", "b1", "c1"],[1, 2, 3]]
	# 	s.write(data = dat, overwrite = True)
	# 	s.copy()
	# 	newfilename = self.classname + self.separator + self.get_func_name() + FileStorage.POSTFIX + self.ext
	# 	self.assertTrue(os.path.exists(self.tmpdir + newfilename))
	# 	s.remove()
    #
	# def test_copy_path(self):
	# 	testfile = self.classname + self.separator + self.get_func_name() + self.ext
	# 	s = Excel2007Storage(self.tmpdir + testfile, sheetIndex = 0)
	# 	s.remove(force = True)
	# 	s.create()
	# 	dat = [["a11", "b11", "c11"],[1, 2, 3]]
	# 	s.write(data = dat, overwrite = True)
	# 	newpath = self.tmpdir + os.path.sep + "test_copy2.xlsx"
	# 	s.copy(path = newpath)
	# 	self.assertTrue(os.path.exists(newpath))
	# 	s.remove()
	# 	Excel2007Storage(newpath, sheetIndex = 0).remove()
    #
	# def test_remove(self):
	# 	with self.assertRaises(StorageNotFoundError):
	# 		s = Excel2007Storage(r"tests/test_data/test_notexists.xlsx", sheetIndex = 0)
	# 		s.remove()
	# 	s = Excel2007Storage(r"tests/test_data/test_todel.xlsx", sheetIndex = 0)
	# 	s.create()
	# 	s.remove()
    #
	# def test_clear(self):
	# 	pass


def suite():
	suite = unittest.TestSuite()
	suite.addTest(Excel2007StorageTest("test_create_file_not_exists"))
	suite.addTest(Excel2007StorageTest("test_create_file_exists"))
	suite.addTest(Excel2007StorageTest("test_create_file_exists_force"))
	suite.addTest(Excel2007StorageTest("test_read"))
	suite.addTest(Excel2007StorageTest("test_read_limit"))
	suite.addTest(Excel2007StorageTest("test_write_append"))
	suite.addTest(Excel2007StorageTest("test_write_overwrite"))
	suite.addTest(Excel2007StorageTest("test_copy"))
	suite.addTest(Excel2007StorageTest("test_copy_path"))
	return suite

if __name__ == "__main__":
	unittest.main(defaultTest = "suite")
