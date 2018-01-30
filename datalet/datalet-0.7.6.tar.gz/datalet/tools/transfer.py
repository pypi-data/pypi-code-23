#!/usr/bin/env python
# -*- coding: utf-8  -*-

from sqlalchemy import create_engine

import datalet.utils.sql_utils

sql = None
mysql_db_url = sql_utils.create_mysql_sqlalchemy_dburl(
	"10.52.27.40",
	"yueyuefa",
	"yueyuefa",
	"123456",
	port = 8866)

engine = create_engine(mysql_db_url)
resultProxy = engine.execute(sql)
for key in resultProxy.keys():
	print(key)
