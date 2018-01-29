#!/usr/bin/env python
# -*- coding: utf-8  -*-

import unittest

class ModelMetaClass(type):
	def __new__():
		# get all columns
		attrs["getColumns"] = None







class DbTableStorage(Storage, metaclass = ModelMetaClass):

	from sqlalchemy import create_engine
	from sqlalchemy import text

	def __delete(self):
		pass

	def __delete_cascade(self):
		pass

	def __drop(self):
		pass

	def __drop_cascade(self):
		pass

	def clear(self, force = False):
		if force == False:
			self.__delete()
		else:
			self.__delete_cascade()


	def remove(self, force = False):
		if force == False:
			self.__drop()
		else:
			self.__drop_cascade()


	def __create_if_not_exist(self):
		pass

	def __create(self):
		pass


class Column(object):
	pass


class DbColumn(Column):
	pass

class BankModel(DbTableStorage):
	__schemaname__ = "testdb"
	__tablename__ = "banks"

	code = DbColumn(name = "code", nullable = False)
	name = DbColumn(name = "name", nullable = False)

class CardFactModel(DbTableStorage):
	__schemaname__ = "testdb"
	__tablename__ = "card_fact_tbl"

	date = DbColumn(name="date", nullable = True)
	src_type = DbColumn(name="type", nullable = True)
	bank_code = DbColumn(name = "bank_code")

	batch_code = DbCOlumn(name = "batch_code")



class SimpleFlowTest(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_from_excel_to_postgres(self):
		# extract
		file_path = "data/test.xlsx"
		sheetIndex = 0
		df_src = excelExtractor.extract(filepath = file_path, sheetIndex = 0)

		# transform
		#card_fact =

		# load
		#db_url = ""
		#db_username = ""
		#db_userpwd = ""
		#loadRules = [
		#	Rule(column = "日期", type = Types.Date, targetField = "date", emptyHandler, unmatchHandler)
		#	, Rule(column = "类型", type = Types.Enum, targetField = "type", emptyHandler, unmatchHandler, saveRawField = "type_raw")
		#	, Rule(column = "银行", type = Types.String, targetField = "bank", emptyHandler, unmatchHandler, saveRawField = "bank_raw")
		#	, Rule(column = "卡类型", type = Types.Enum, targetField = "cardtype", emptyHandler, unmatchHandler, saveRawField = "cardtype_raw")
		#	, Rule(column = "用户数", type = Types.Integer, targetField = "usersCount", emptyHandler, unmatchHandler)
		#	, Rule(column = "卡数", type = Types.Integer, targetField = "cardsCount", emptyHandler, unmatchHandler)
		#]
		#tableLoadRule = TableLoadRule(targetSchemaName = "jd_sys", targetTableName="users", autoCreateSchema = True, appendType = AppendType.AppendAfterCleanCascade)
		#tableLoadRule.addColumnRule(ColumnRule(sourceColumn = "日期", datatype = DataTypes.Date, targetField = "date", emptyHandler = ignoreEmptyHandler, unmatchHandler = alertUnmatchHander))

		#loader = Loader(data = dat ,rules = loadRules, recreateSchema = True)
		# self.assertEqual(1, 2)


def suite():
	suite = unittest.TestSuite()
	suite.addTest(SimpleFlowTest("test_from_excel_to_postgres"))
	return suite

if __name__ == "__main__":
	unittest.main(defaultTest = "suite")
