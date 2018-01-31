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
from datalet.data import *
import datalet.utils.inspect_utils as inspect_utils

#sys.setdefaultencoding('utf8')

class CsvStorageTest(unittest.TestCase):

	def setUp(self):
		self.tmpdir = r"tests/test_data/tmp/"
		self.classname = self.__class__.__name__
		self.separator = "$"
		self.ext = ".csv"

		self.dt = DataTable(columns = ['a', 'b', 'c'], rows = [[1, 2, 3]])

	def tearDown(self):
		pass

	def test_create_file_not_exists(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.create(force = True)
		self.assertTrue(os.path.exists(s.location))
		s.remove(force = True)
		self.assertTrue(not os.path.exists(s.location))

	def test_create_file_exists(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.create(force = True)
		with self.assertRaises(StorageExistedError):
			s.create()
		s.remove(force = True)
		self.assertTrue(not os.path.exists(s.location))

	def test_create_file_exists_force(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.create(force = True)
		self.assertTrue(os.path.exists(s.location))
		s.create(force = True)
		self.assertTrue(os.path.exists(s.location))
		s.remove(force = True)
		self.assertTrue(not os.path.exists(s.location))

	def test_read(self):
		s = CsvStorage(r"tests/test_data/test.csv")
		dat = s.read(encoding = "utf-8")
		self.assertTrue(len(dat) > 0)

	def test_read_limit(self):
		s = CsvStorage(r"tests/test_data/test.csv")
		dat = s.read(limit = 7)
		self.assertTrue(len(dat) == 7)

	def test_write_append(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		if not s.exists():
			s.create()
		dat = s.read()
		s.write(data = self.dt)
		dat2 = s.read()
		self.assertTrue(len(dat2) > len(dat))


	def test_write_overwrite(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.create(force = True)
		s.write(data = self.dt, overwrite = True)
		dat = s.read()
		self.assertTrue(len(dat) == 2)

	def test_copy_path(self):
		testfile = self.classname + self.separator + inspect_utils.get_current_func_name() + self.ext
		s = CsvStorage(self.tmpdir + testfile)
		s.create(force = True)
		s.write(data = self.dt, overwrite = True)
		newpath = self.tmpdir + os.path.sep + "test_copy2.csv"
		s.copy(copy_to_path = newpath)
		self.assertTrue(os.path.exists(newpath))
		s.remove()
		CsvStorage(newpath).remove()
		self.assertTrue(not os.path.exists(newpath))

	def test_remove(self):
		with self.assertRaises(StorageNotFoundError):
			s = CsvStorage(r"tests/test_data/test_notexists.csv")
			s.remove()
		s = CsvStorage(r"tests/test_data/test_todel.csv")
		s.create(force = True)
		s.remove(force = True)
		self.assertTrue(not os.path.exists(s.location))

	def test_clear(self):
		pass
