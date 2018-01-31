#!/usr/bin/env python
# -*- coding: utf-8  -*-

import sys
sys.path.insert(0, r"../datalet")

import os
import unittest

import datalet.storage.facade as sfd
from tests.testing import Testing

class FacadeTest(unittest.TestCase):

	def setUp(self):
		self.tmpdir = r"tests/test_data/tmp/"
		self.classname = self.__class__.__name__
		self.separator = "$"

	def tearDown(self):
		pass

	# def test_create_file(self):
	# 	for type in sfd.StorageTypes:
	# 		if type == sfd.StorageTypes.DATABASE:
	# 			continue
    #
	# 		testfile = self.classname + self.separator + self.get_func_name() + "." + type.name.lower()
	# 		testfile_fullpath = self.tmpdir + testfile
	# 		if sfd.exists_file(testfile_fullpath):
	# 			sfd.remove_file(testfile_fullpath, force = True)
    #
	# 		sfd.create_file(testfile_fullpath)
	# 		self.assertTrue(os.path.exists(testfile_fullpath))
    #
	# def test_read_file(self):
	# 	for type in sfd.StorageTypes:
	# 		if type == sfd.StorageTypes.DATABASE:
	# 			continue
    #
	# 		testfile_fullpath = r"tests/test_data/test." + type.name.lower()
	# 		dat = sfd.read_file(testfile_fullpath, sheetIndex = 0)
	# 		print(dat[:4])
	# 		self.assertTrue(len(dat) > 0)
    #
	# def test_write_file(self):
	# 	data = [["姓名", "年龄", "班级"], ["小花", 13, 3], ["小蕊", 14, 4]]
	# 	for type in sfd.StorageTypes:
	# 		if type == sfd.StorageTypes.DATABASE:
	# 			continue
	# 		testfile = self.classname + self.separator + self.get_func_name() + "." + type.name.lower()
	# 		testfile_fullpath = self.tmpdir + testfile
	# 		if not sfd.exists_file(testfile_fullpath):
	# 			sfd.create_file(testfile_fullpath, force = True)
	# 		try:
	# 			sfd.write_file(testfile_fullpath, data = data, overwrite = False, encoding = "gbk", sheetIndex = 0)
	# 		except NotImplementedError as err:
	# 			pass
	# 		finally:
	# 			pass

def suite():
	suite = unittest.TestSuite()
	suite.addTest(FacadeTest("test_create_file"))
	suite.addTest(FacadeTest("test_read_file"))
	suite.addTest(FacadeTest("test_write_file"))
	return suite

if __name__ == "__main__":
	unittest.main(defaultTest = "suite")
