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

class DataTableTesting(Testing):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_integer_index(self):
		dt = DataTable("mytable", DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age"))
		dt.append(["zhangsan", "boy", 24])
		dt.append(["lisi", "girl", 30])
		dt.append(["wangwu", "boy", 33])

		#self.assertTrue(dt[1].name == "lisi")

	def test_iter(self):
		dt = DataTable("mytable", DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age"))
		dt.append(["zhangsan", "boy", 24])
		dt.append(["lisi", "girl", 30])
		dt.append(["wangwu", "boy", 33])

		for col in dt.columns:
			print("column's name: " , col.name)

		for row in dt:
			for data in row:
				print(data)

	def test_to_dict(self):
		dt = DataTable("mytable", DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age"))
		dt.append(["zhangsan", "boy", 24])
		dt.append(["lisi", "girl", 30])
		dt.append(["wangwu", "boy", 33])
		dt.append(["zhaoqi", None, None])
		print(list(dt.to_dict()))


	def test_append_row(self):
		dt = DataTable("mytable", DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age"))
		dt.append(["zhangsan", "boy", 24])
		dt.append(("lisi", "girl", 30))
		dt.append({"name":"wangwu", "sex":"boy", "age":33})
		dt.append(["zhaoqi", None, None])
		print(list(dt.to_dict()))


	def test_get_data_by_column(self):
		dt = DataTable("mytable", DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age"))
		dt.append(["zhangsan", "boy", 24])
		dt.append(("lisi", "girl", 30))
		dt.append({"name":"wangwu", "sex":"boy", "age":33})
		dt.append(["zhaoqi", None, None])
		print(list(dt["name"]))

	def test_del_data_by_index(self):
		dt = DataTable("mytable", DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age"))
		dt.append(["zhangsan", "boy", 24])
		dt.append(("lisi", "girl", 30))
		dt.append({"name":"wangwu", "sex":"boy", "age":33})
		dt.append(["zhaoqi", None, None])
		print(len(dt))
		del dt[0]
		print(len(dt))


def suite():
	suite = unittest.TestSuite()
	suite.addTest(DataTableTesting("test_integer_index"))
	suite.addTest(DataTableTesting("test_iter"))
	suite.addTest(DataTableTesting("test_to_dict"))
	suite.addTest(DataTableTesting("test_append_row"))
	suite.addTest(DataTableTesting("test_get_data_by_column"))
	suite.addTest(DataTableTesting("test_del_data_by_index"))
	return suite

if __name__ == "__main__":
	unittest.main(defaultTest = "suite")
