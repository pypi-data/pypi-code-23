#!/usr/bin/python
#-*-coding:utf-8-*-

import json
import pymysql
# import sys;
# sys.path.append(".")
from . import Table
from . import Column

__author__ = 'skydu'

class MysqlDiff(object):
    #
    def getComment(self,comment):
        if comment==None:
            return ""
        try:
            data=json.loads(comment)
            return data[0]['value']
        except:
            return comment

    def getTables(self,db,dbName):
        sql = "select table_name, TABLE_COMMENT from information_schema.tables " \
              "where table_schema = '%s' and table_type = 'base table'"%dbName
        cursor=db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        tables={}
        for table in data:
            t=Table(table[0], self.getComment(table[1]));
            tables[table[0]]=t
        cursor.close()
        return tables

    def getColumns(self,db,dbName,tableName):
        sql = "SELECT  " \
              "COLUMN_NAME 列名,  " \
              "COLUMN_TYPE 数据类型,  " \
              "IS_NULLABLE 是否为空,    " \
              "COLUMN_DEFAULT 默认值,    " \
              "COLUMN_COMMENT 备注   " \
              "FROM  INFORMATION_SCHEMA.COLUMNS  " \
              "where  table_schema ='%s'  AND   table_name  = '%s';" % (dbName, tableName)
        cursor = db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        columns={}
        for column in data:
            c=Column(column[0],column[1],column[2],column[3],self.getComment(column[4]))
            columns[column[0]]=c
        cursor.close()
        return columns

    def test(self):
        self.diff('127.0.0.1','root','','db_test1',8001,
                '127.0.0.1','root','','db_test2',8001)

    def diff(self,dbHost, dbUser, dbPassword, dbName, dbPort,dbHost2, dbUser2, dbPassword2, dbName2, dbPort2):
        print("dbHost:%s,dbUser:%s,dbPassword:%s,dbName:%s,dbPort:%d" % (dbHost, dbUser, dbPassword, dbName, dbPort))
        print("dbHost2:%s,dbUser2:%s,dbPassword2:%s,dbName2:%s,dbPort2:%d" % (dbHost2, dbUser2, dbPassword2, dbName2, dbPort2))
        db = pymysql.connect(dbHost, dbUser, dbPassword, dbName, dbPort, charset="utf8")
        db2 = pymysql.connect(dbHost2, dbUser2, dbPassword2, dbName2, dbPort2, charset="utf8")
        tables = self.getTables(db,dbName);
        tables2 = self.getTables(db2,dbName2);
        self.diffTables(1,db2,db,dbName2,dbName,tables2,tables)
        self.diffTables(2,db,db2,dbName,dbName2,tables,tables2)

    def diffTables(self,index,db,db2,dbName,dbName2,tables,tables2):
        print("====================db%d[%s] difference============================"%(index,dbName2))
        for tableName, table in tables.items():
            if tableName in tables2:
                table2 = tables2[tableName]
                table.columns = self.getColumns(db, dbName, tableName)
                table2.columns = self.getColumns(db2, dbName2, tableName)
                for columnName, column in table.columns.items():
                    if columnName in table2.columns:
                        continue
                    print("%s miss column %s" % (tableName, columnName))
            else:
                print("miss table %s" % (tableName))