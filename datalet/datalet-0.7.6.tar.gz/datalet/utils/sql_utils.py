#!/usr/bin/env python
# -*- coding: utf-8  -*-

def create_pgsql_sqlalchemy_dburl(host, dbname, user, pwd, port = 5432):
	return "postgresql+psycopg2://%s:%s@%s:%d/%s" % (user, pwd, host, port, dbname)

def create_mysql_sqlalchemy_dburl(host, dbname, user, pwd, port = 3306):
	return "mysql+pymysql://%s:%s@%s:%d/%s?charset=utf8" % (user, pwd, host, port, dbname)

def create_oracle_sqlalchemy_dburl(host, dbname, user, pwd, port = 1521):
	return NotImplementedError

def create_sqlite_sqlalchemy_dburl(host, dbname, user, pwd, port = 5432):
	return NotImplementedError

def create_mssql_sqlalchemy_dburl(host, dbname, user, pwd, port = 1433):
	return NotImplementedError
