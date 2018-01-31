#!/usr/bin/env python
# -*- coding: utf-8  -*-

"""
execute the unittest file in project root directory.
"""
import sys
sys.path.insert(0, r"../datalet")

import os
import unittest

from sqlalchemy import Table, Column, Integer, String, MetaData, TIMESTAMP, DECIMAL, BigInteger

from datalet.data import *
from datalet.storage.dbtable_storage import *
from datalet.storage.excel_storage import ExcelStorage
from tests.testing import Testing
import datalet.utils.sql_utils as sql_utils

metadata = MetaData()

class DbTableStorageTest(unittest.TestCase):

	def setUp(self):
		self.tmpdir = r"tests/test_data/tmp/"
		self.classname = self.__class__.__name__
		self.separator = "$"
		self.ext = ".csv"

		self.host = "localhost"
		self.dbname = "testdb"
		self.user = "pgadmin"
		self.pwd = "pgadmin."

		#self.host = "localhost"
		#self.dbname = "testdb"
		#self.user = "pgdba"
		#self.pwd = "pgdba"


		self.table = Table("test_table", metadata,
					 Column("code", String(100), nullable = False),
					 Column("name", String(100), nullable = True),
					 Column("create_date", TIMESTAMP, nullable = False),
					 extend_existing=True,
					 schema = "test_schema")

	def tearDown(self):
		pass

	# def test_create_pg_dburl(self):
	# 	url = sql_utils.create_pg_sqlalchemy_dburl(host="localhost", dbname="testdb", user="pgadmin", pwd="pgadmin123")
	# 	self.assertEqual("postgresql+psycopg2://pgadmin:pgadmin123@localhost:5432/testdb", url)
    #
	# def test_create_table_force_true(self):
	# 	dburl = sql_utils.create_pg_sqlalchemy_dburl(host = self.host, dbname = self.dbname, user = self.user, pwd = self.pwd)
	# 	s = DbTableStorage(dburl, table=self.table)
	# 	self.assertEqual(s.create(force = True), None)
    #
	# def test_create_table_force_false(self):
	# 	dburl = sql_utils.create_pg_sqlalchemy_dburl(host = self.host, dbname = self.dbname, user = self.user, pwd = self.pwd)
	# 	s = DbTableStorage(dburl, table=self.table)
	# 	with self.assertRaises(StorageExistsError):
	# 		s.create(force = False)
    #
	# def test_write_data_overwrite_true(self):
	# 	dburl = sql_utils.create_pg_sqlalchemy_dburl(host = self.host, dbname = self.dbname, user = self.user, pwd = self.pwd)
	# 	s = DbTableStorage(dburl, table=self.table)
	# 	data = [{"code": "ACF1001", "name": "lisi", "create_date": "2016-01-01"},
	# 	  {"code": "ACF1002", "name": "zhangsan", "create_date": "2016-01-02"},
	# 	  {"code": "ACF1003", "name": "wangwu", "create_date": "2016-01-03"}]
	# 	s.write(data, overwrite = True)
	# 	#s.write(data, overwrite = False)
	# 	#s.write(data, overwrite = True)
    #
	# def test_write_data_by_batch(self):
	# 	dburl = sql_utils.create_pg_sqlalchemy_dburl(host = self.host, dbname = self.dbname, user = self.user, pwd = self.pwd)
	# 	s = DbTableStorage(dburl, table=self.table)
	# 	s.create(force = True)
	# 	data = []
	# 	for i in range(0, 100):
	# 		d = {"code": "CODE_" + str(i), "name": "NAME_" + str(i), "create_date": "2016-01-01"}
	# 		data.append(d)
	# 	batch_rows_count = 32
	# 	s.write(data, batch_rows_count = batch_rows_count)
    #
	# def test_write_data_transaction(self):
	# 	dburl = sql_utils.create_pgsql_sqlalchemy_dburl(host = self.host, dbname = self.dbname, user = self.user, pwd = self.pwd)
	# 	s = DbTableStorage(dburl, table=self.table)
	# 	if not s.exists():
	# 		s.create(force = False)
	# 	data = []
	# 	for i in range(0, 100):
	# 		d = {"code": "CODE_" + str(i), "name": "NAME_" + str(i), "create_date": "2016-01-01"}
	# 		data.append(d)
	# 	batch_rows_count = 20
	# 	s.write(data, batch_rows_count = batch_rows_count)
    #
	# def test_read_no_limit(self):
	# 	dburl = sql_utils.create_pg_sqlalchemy_dburl(host = self.host, dbname = self.dbname, user = self.user, pwd = self.pwd)
	# 	s = DbTableStorage(dburl, table=self.table)
	# 	for row in s.read():
	# 		print(row)

	# def test_write_large_data(self):
	# 	import pandas as pd
	# 	excel = ExcelStorage(location = r"D:\svnserver\业务数据\数据库同步数据\交易数据交易数据_1607_new.xlsx", sheet_name = "交易")
	# 	#excel = ExcelStorage(filepath = r"D:\正单_TEST.xlsx", sheetIndex = 1)
	# 	datatable = excel.read()
	# 	datatable.shift_rows_to_header(1)
	# 	df_data = datatable.to_pandas_dataframe()
	# 	print("Got dataframe.")
	# 	df_data = df_data.rename(columns = {"会计时间": "fiscal_date",
	# 								  "商户ID": "mer_id",
	# 								  "商户名称": "mer_name",
	# 								  "交易名称": "trade_name",
	# 								  "交易类型": "trade_type",
	# 								  "交易状态": "trade_status",
	# 								  "模式名称": "mode_name",
	# 								  "支付工具": "pay_tools",
	# 								  "业务名称": "pay_biz_name",
	# 								  "卡类型": "cardtype",
	# 								  "卡类型名称": "cardtype_name",
	# 								  "发卡行": "send_bank_code",
	# 								  "收单行": "recv_bank_code",
	# 								  "银行商户号": "bank_mer_code",
	# 								  "银行清算时间": "bank_clr_time",
	# 								  "笔数": "orders_count",
	# 								  "金额": "orders_money",
	# 								  "商户手续费": "mer_fee",
	# 								  "业务名称_处理后": "biz_name_proced",
	# 								  "银行名称_处理后": "bank_name_proced",
	# 								  "卡类型_处理后": "cardtype_name_proced",
	# 								  "名义费率_处理后": "nominal_rate",
	# 								  "名义成本_处理后": "nominal_cost",
	# 								  "1级所属类型_处理后": "biz_level_1st",
	# 								  "2级所属类型_处理后": "biz_level_2nd",
	# 								  "3级所属类型_处理后": "biz_level_3rd"})
	# 	df_wanted = df_data.loc[:, ["fiscal_date",
	# 					  "mer_id",
	# 					  "mer_name",
	# 					  "trade_name",
	# 					  "trade_type",
	# 					  "trade_status",
	# 					  "mode_name",
	# 					  "pay_tools",
	# 					  "pay_biz_name",
	# 					  "cardtype",
	# 					  "cardtype_name",
	# 					  "send_bank_code",
	# 					  "recv_bank_code",
	# 					  "bank_mer_code",
	# 					  "bank_clr_time",
	# 					  "orders_count",
	# 					  "orders_money",
	# 					  "mer_fee",
	# 					  "biz_name_proced",
	# 					  "bank_name_proced",
	# 					  "cardtype_name_proced",
	# 					  "nominal_rate",
	# 					  "nominal_cost",
	# 					  "biz_level_1st",
	# 					  "biz_level_2nd",
	# 					  "biz_level_3rd"]]
	# 	df_wanted["orders_count"] = df_wanted["orders_count"].astype(object)
	# 	print(df_wanted)
    #
	# 	tb = Table("large_table", metadata,
	# 				 Column("fiscal_date", TIMESTAMP, nullable = True),
	# 				 Column("mer_id", String(100), nullable = True),
	# 				 Column("mer_name", String(100), nullable = True),
	# 				 Column("trade_name", String(100), nullable = True),
	# 				 Column("trade_type", String(100), nullable = True),
	# 				 Column("trade_status", String(100), nullable = True),
	# 				 Column("mode_name", String(100), nullable = True),
	# 				 Column("pay_tools", String(100), nullable = True),
	# 				 Column("pay_biz_name", String(100), nullable = True),
	# 				 Column("cardtype", String(100), nullable = True),
	# 				 Column("cardtype_name", String(100), nullable = True),
	# 				 Column("send_bank_code", String(100), nullable = True),
	# 				 Column("recv_bank_code", String(100), nullable = True),
	# 				 Column("bank_mer_code", String(100), nullable = True),
	# 				 Column("bank_clr_time", TIMESTAMP, nullable = True),
	# 				 Column("orders_count", BigInteger, nullable = True),
	# 				 Column("orders_money", DECIMAL, nullable = True),
	# 				 Column("mer_fee", DECIMAL, nullable = True),
	# 				 Column("biz_name_proced", String(100), nullable = True),
	# 				 Column("bank_name_proced", String(100), nullable = True),
	# 				 Column("cardtype_name_proced", String(100), nullable = True),
	# 				 Column("nominal_rate", String(100), nullable = True),
	# 				 Column("nominal_cost", DECIMAL, nullable = True),
	# 				 Column("biz_level_1st", String(100), nullable = True),
	# 				 Column("biz_level_2nd", String(100), nullable = True),
	# 				 Column("biz_level_3rd", String(100), nullable = True),
	# 				 extend_existing=True,
	# 				 schema = "test_schema")
	# 	dburl = sql_utils.create_pg_sqlalchemy_dburl(host = self.host, dbname = self.dbname, user = self.user, pwd = self.pwd)
	# 	s = DbTableStorage(dburl, table = tb)
	# 	if not s.exists():
	# 		s.create(force = False)
	# 	#print("start to build dict.")
	# 	#df_wanted["orders_count"] = df_wanted["orders_count"].astype(object)
	# 	#df_wanted = df_wanted.applymap(proc_nan)
	# 	#print(df_wanted[:5].to_dict(orient = "records"))
	# 	#print(df_wanted.dtypes)
	# 	#dict_data = df_wanted.to_dict(orient = "records")
	# 	#print("succeed in building dict.")
	# 	new_table = DataTable()
	# 	new_table.from_pandas_dataframe(df_wanted)
	# 	dict_data = new_table.to_dict(null_expr = None)
	# 	s.write(dict_data, batch_rows_count = 100)
	# 	print("succeed in writing to db.")


def suite():
	suite = unittest.TestSuite()
	#suite.addTest(DbTableStorageTest("test_create_pg_dburl"))
	#suite.addTest(DbTableStorageTest("test_create_table_force_true"))
	#suite.addTest(DbTableStorageTest("test_create_table_force_false"))
	#suite.addTest(DbTableStorageTest("test_write_data_overwrite_true"))
	#suite.addTest(DbTableStorageTest("test_write_data_by_batch"))
	#suite.addTest(DbTableStorageTest("test_write_data_transaction"))
	#suite.addTest(DbTableStorageTest("test_read_no_limit"))
	suite.addTest(DbTableStorageTest("test_write_large_data"))
	return suite

if __name__ == "__main__":
	unittest.main(defaultTest = "suite")
