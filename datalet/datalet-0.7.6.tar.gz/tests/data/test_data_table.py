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

class DataTableTesting(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_init(self):
		dt1 = DataTable()

	def test_integer_index(self):
		dt = DataTable("mytable", [ DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age")])
		dt.append(["zhangsan", "boy", 24])
		dt.append(["lisi", "girl", 30])
		dt.append(["wangwu", "boy", 33])
		self.assertTrue(dt[1]["sex"] == "girl")

	def test_iter(self):
		dt = DataTable("mytable", [ DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age")])
		dt.append(["zhangsan", "boy", 24])
		dt.append(["lisi", "girl", 30])
		dt.append(["wangwu", "boy", 33])

		ret_column_names = []
		for col in dt.columns:
			ret_column_names.append(col.name)
		self.assertTrue(ret_column_names == ['name', 'sex', 'age'])

		ret_rows_data = []
		for row in dt:
			row_data = []
			for data in row:
				row_data.append(data)
			ret_rows_data.append(row_data)
		self.assertTrue(len(ret_rows_data) == 3)

	def test_to_dict(self):
		dt = DataTable("mytable", [ DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age")])
		dt.append(["zhangsan", "boy", 24])
		dt.append(["lisi", "girl", 30])
		dt.append(["wangwu", "boy", 33])
		dt.append(["zhaoqi", None, None])
		self.assertTrue(isinstance(list(dt.to_dict())[0], dict))


	def test_append_row(self):
		dt = DataTable("mytable", [ DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age")])
		dt.append(["zhangsan", "boy", 24])
		dt.append(("lisi", "girl", 30))
		dt.append({"name":"wangwu", "sex":"boy", "age":33})
		dt.append(["zhaoqi", None, None])
		self.assertTrue(isinstance(list(dt.to_dict())[0], dict))


	def test_get_data_by_column(self):
		dt = DataTable("mytable", [DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age")])
		dt.append(["zhangsan", "boy", 24])
		dt.append(("lisi", "girl", 30))
		dt.append({"name":"wangwu", "sex":"boy", "age":33})
		dt.append(["zhaoqi", None, None])
		self.assertTrue(list(dt["name"]) == ['zhangsan', 'lisi', 'wangwu', 'zhaoqi'])

	def test_del_data_by_index(self):
		dt = DataTable("mytable", [DataColumn("name"), DataColumn(name = "sex"), DataColumn(name = "age")])
		dt.append(["zhangsan", "boy", 24])
		dt.append(("lisi", "girl", 30))
		dt.append({"name":"wangwu", "sex":"boy", "age":33})
		dt.append(["zhaoqi", None, None])
		self.assertTrue(len(dt) == 4)
		del dt[0]
		self.assertTrue(len(dt) == 3)


	def test_from_list(self):
		ls = [['name', 'age'], ['zhangsan', 29]]
		dt = DataTable.from_list(src_list = ls)
		self.assertTrue(dt[0]['name'] == 'zhangsan')


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
