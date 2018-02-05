# -*- coding: utf-8 -*-
"""
@author: weber.juche@gmail.com
@time: 2017/1/4 13:57

    数据库访问游标类封装
    ~~~~~~~~~~~~~~~~~~
"""
import sys
from weberFuncs import PrintTimeMsg
#--------------------------------------
class CDBCursor(object):
    """
        数据库访问游标类
    """
    def __init__(self, dbConnection):
        # dbConnection 是 CDBConnection 的实例
        self.dbConnection = dbConnection
        self.oConn = None
        self.oCursor = None

    def __del__(self):
        self.cursorClose()

    def __enter__(self):
        # with as 语句入口处理
        # PrintTimeMsg('CDBCursor.__enter__')
        return self.cursorOpen()

    def __exit__(self, type, value, traceback):
        # with as 语句出口处理
        # PrintTimeMsg('CDBCursor.__exit__(%s,%s,%s)' % (type, value, traceback))
        self.cursorClose()

    def cursorOpen(self):
        # 打开游标
        self.oConn = self.dbConnection.getConnection()
        if (not self.oCursor) or (self.oCursor.open):
            PrintTimeMsg("cursorOpen(%s,%s)..." % (self.dbConnection.sEngine,self.dbConnection.sConnHint))
            self.oCursor = self.oConn.cursor()
        return self.oConn,self.oCursor

    def cursorClose(self):
        # 打开关闭
        if self.oCursor:
            PrintTimeMsg("cursorClose(%s,%s)..." % (self.dbConnection.sEngine,self.dbConnection.sConnHint))
            self.oCursor.close()
            self.oCursor = None
        else:
            PrintTimeMsg("cursorClose(%s,%s).oCursor=NULL" % (self.dbConnection.sEngine,self.dbConnection.sConnHint))

#--------------------------------------
def TestCDBCursorInit():
    # 测试类创建模式使用游标
    from CDBConnection import CDBConnection
    from testDictParam import ReturnMysqlDictParamDB

    conn = CDBConnection(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test")
    cur = CDBCursor(conn)
    cur.oConn = cur.dbConnection.getConnection()
    cur.oCursor = cur.oConn.cursor()
    sSQL = 'select version()'
    oRet = cur.oCursor.execute(sSQL)
    PrintTimeMsg('SqlExecute(%s)=(%s)' % (sSQL,oRet))
    return

def TestCDBCursorWith1():
    # 测试 with 语句访问游标
    from CDBConnection import CDBConnection
    from testDictParam import ReturnMysqlDictParamDB

    dbConn = CDBConnection(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test")
    with CDBCursor(dbConn) as (conn,cursor):
        sSQL = 'select version()'
        oRet = cursor.execute(sSQL)
        PrintTimeMsg('SqlExecute(%s)=(%s)' % (sSQL,oRet))
        print cursor
        return

def TestCDBCursorWith2():
    # 测试 with 语句访问游标
    from CDBConnection import CDBConnection
    from testDictParam import ReturnMysqlDictParamDB

    with CDBConnection(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test") as dbConn:
        with CDBCursor(dbConn) as (conn,cursor):
            sSQL = 'select version()'
            oRet = cursor.execute(sSQL)
            PrintTimeMsg('SqlExecute(%s)=(%s)' % (sSQL,oRet))
            print cursor
            return

#--------------------------------------
if __name__ == '__main__':
    # TestCDBCursorInit()
    # TestCDBCursorWith1()
    TestCDBCursorWith2()
