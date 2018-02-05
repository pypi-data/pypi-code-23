# -*- coding: utf-8 -*-
"""
@author: weber.juche@gmail.com
@time: 2017/1/4 15:08

    数据库SQL语句操作封装
    ~~~~~~~~~~~~~~~~~~~~
"""
import sys
from weberFuncs import PrintTimeMsg,GetCurrentTime,PrettyPrintObj

#--------------------------------------
#--------------------------------------
class CSQLBase(object):
    # 添加数据库基本操作

    def __init__(self, dbConn, conn, cursor):
        """
            :param dbConn: 是 CDBConnection 的实例
            :param conn, cursor 是 CDBCursor with as 返回的游标
        """
        self.dbConn = dbConn
        self.oConn  = conn
        self.oCursor = cursor

    def sqlExecuteOne(self,sSQL, lsData=[]):
        # 执行SQL语句，由调用者处理异常
        # 成功返回执行结果，出错抛出异常
        # WeiYF.20170104 经测试，若执行增删改语句后没有提交，则不会生效
        oRet = self.oCursor.execute(sSQL, lsData)
        PrintTimeMsg('sqlExecuteOne(%s)=(%s)' % (sSQL,oRet))
        return oRet

    def sqlInsertOne(self, sSQL, lsData=[]):
        # 插入单条记录
        # 成功返回True，索引重复返回False，其余继续抛出异常
        try:
            oRet = self.sqlExecuteOne(sSQL, lsData)
            if oRet==1: return True # 插入成功返回
            PrintTimeMsg('sqlInsertOne(%s)=(%s)' % (sSQL,oRet))
            return False
        except Exception as e:
            if self.dbConn.checkIsInsertEXT(e):
                PrintTimeMsg('sqlInsertOne.checkIsInsertEXT(%s)=(%s)' % (sSQL,str(e)))
                return False
            raise

    def _sqlUpdDelOne(self, sUpdDel, sSQL, lsData=[]):
        # 修改或删除单条记录
        # 成功返回True，没有找到对应记录或者匹配多条返回False，其余继续抛出异常
        try:
            oRet = self.sqlExecuteOne(sSQL, lsData)
            if oRet==1: return True # 插入成功返回
            PrintTimeMsg('_sqlUpdDelOne(%s,%s)=(%s)' % (sUpdDel,sSQL,oRet))
            return False
        except Exception as e:
            raise

    def sqlUpdateOne(self, sSQL, lsData=[]):
        # 修改单条记录
        return self._sqlUpdDelOne('Upd',sSQL, lsData)

    def sqlDeleteOne(self, sSQL, lsData=[]):
        # 删除单条记录
        return self._sqlUpdDelOne('Del',sSQL, lsData)

    def sqlInsUpdOne(self, sInsSQL, sUpdSQL, lsData=[]):
        # 单条记录，插入重复则修改
        bRet = self.sqlInsertOne(sInsSQL, lsData)
        if bRet: return bRet
        return self.sqlUpdateOne(sUpdSQL, lsData)

    def sqlSelectOne(self, sSQL):
        # 查询单条记录
        # 成功返回字段列表，没有找到或匹配多条返回False，其余继续抛出异常
        try:
            oRet = self.sqlExecuteOne(sSQL)
            if oRet==1:
                lsResult = list(self.oCursor.fetchone())
                PrintTimeMsg('sqlSelectOne(%s)=(%s)' % (sSQL,lsResult))
                return lsResult # 插入成功返回
            PrintTimeMsg('sqlSelectOne(%s)=(%s)' % (sSQL,oRet))
            return []
        except Exception as e:
            raise

#--------------------------------------
def TestCSQLBase():
    from cursorFuncs import ProcessCursorFunc
    from testDictParam import ReturnMysqlDictParamDB
    # with CDBConnection(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test") as conn:
    #     with CDBCursor(conn) as cursor:
    def cbTest(dbConn,conn,cursor):
        o = CSQLBase(dbConn,conn,cursor)
        oRet = o.sqlInsertOne('insert into testtmp values (100, "test100");')
        PrintTimeMsg('sqlInsertOne.insert0=(%s)' % (oRet))
        conn.commit()
        # return
        # 如下语句重复时，会抛出异常
        # oRet = o.sqlExecuteOne('insert into testtmp values (100, "test100");')
        # PrintTimeMsg('sqlInsertOne.insert0=(%s)' % (oRet))
        # conn.commit()
        # return
        oRet = o.sqlInsertOne('insert into testtmp values (100, "test100");')
        PrintTimeMsg('sqlInsertOne.insert1=(%s)' % (oRet))
        conn.commit()

        oRet = o.sqlUpdateOne('update testtmp set name = "test100B" where testid=100;')
        PrintTimeMsg('sqlUpdateOne.1=(%s)' % (oRet))
        conn.commit()

        oRet = o.sqlDeleteOne('delete from testtmp where testid=102;')
        PrintTimeMsg('sqlDeleteOne.1=(%s)' % (oRet))
        conn.commit()


        oRet = o.sqlInsUpdOne('insert into testtmp values (101, "test101A");',
                             'update testtmp set name = "test101B" where testid=101;')
        PrintTimeMsg('sqlInsUpdOne.1=(%s)' % (oRet))
        conn.commit()

        oRet = o.sqlInsertOne('insert into testtmp values (102, "test102");')
        PrintTimeMsg('SqlInsert.insert1=(%s)' % (oRet))
        # conn.sqlRollback()
        # return
        oRet = o.sqlInsertOne('insert into testtmp values (103, "test103");')
        PrintTimeMsg('SqlInsert.insert2=(%s)' % (oRet))
        conn.commit()

        oRet = o.sqlSelectOne('select * from testtmp where testid = 103;')
        PrintTimeMsg('sqlSelectOne.1=(%s)' % (oRet))

        oRet = o.sqlSelectOne('select * from testtmp where testid = 404;')
        PrintTimeMsg('sqlSelectOne.1=(%s)' % (oRet))
        return
    ProcessCursorFunc(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test",cbDealFunc=cbTest)

#--------------------------------------
if __name__ == '__main__':
    # TestCDBConnMBase()
    TestCSQLBase()

