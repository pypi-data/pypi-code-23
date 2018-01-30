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
import datalet.utils.inspect_utils as inspect_utils

#sys.setdefaultencoding('utf8')

class CsvStorageTest(unittest.TestCase):

	def setUp(self):
		self.tmpdir = r"tests/test_data/tmp/"
		self.classname = self.__class__.__name__
		self.separator = "$"
		self.ext = ".csv"

	def tearDown(self):
		pass

	def test_create_file_not_exists(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.remove(force = True)
		s.create()
		s.remove(force = True)

	def test_create_file_exists(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.remove(force = True)
		s.create()
		with self.assertRaises(StorageExistsError):
			s.create()
		s.remove(force = True)


	def test_create_file_exists_force(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.remove(force = True)
		s.create()
		s.create(force = True)
		s.remove(force = True)

	def test_read(self):
		s = CsvStorage(r"tests/test_data/test.csv")
		dat = s.read(encoding = "utf-8")
		self.assertTrue(len(dat) > 0)
		print(">>> totol line count: ", len(dat))
		#for row in dat:
		#	print([cell for cell in row])


	def test_read_limit(self):
		s = CsvStorage(r"tests/test_data/test.csv")
		dat = s.read(limit = 5)
		self.assertTrue(len(dat) == 5)

	def test_write_append(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		if not s.exists():
			s.create()
		dat = [["a", "b", "c"],[1, 2, 3]]
		s.write(data = dat)


	def test_write_overwrite(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.remove(force = True)
		s.create()
		dat = [["a", "b", "c"],[1, 2, 3]]
		s.write(data = dat, overwrite = True)

	def test_copy(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.remove(force = True)
		s.create()
		dat = [["a1", "b1", "c1"],[1, 2, 3]]
		s.write(data = dat, overwrite = True)
		s.copy()
		newfilename = self.classname + self.separator + inspect_utils.get_current_func_name() + FileStorage.POSTFIX + self.ext
		self.assertTrue(os.path.exists(self.tmpdir + newfilename))
		s.remove()

	def test_copy_path(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.remove(force = True)
		s.create()
		dat = [["a11", "b11", "c11"],[1, 2, 3]]
		s.write(data = dat, overwrite = True)
		newpath = self.tmpdir + os.path.sep + "test_copy2.csv"
		s.copy(path = newpath)
		self.assertTrue(os.path.exists(newpath))
		s.remove()
		CsvStorage(newpath).remove()

	def test_remove(self):
		with self.assertRaises(StorageNotFoundError):
			s = CsvStorage(r"tests/test_data/test_notexists.csv")
			s.remove()
		s = CsvStorage(r"tests/test_data/test_todel.csv")
		s.create()
		s.remove()

	def test_clear(self):
		pass
