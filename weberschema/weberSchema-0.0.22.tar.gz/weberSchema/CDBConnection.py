# -*- coding: utf-8 -*-
"""
@author: weber.juche@gmail.com
@time: 2017/1/4 13:27

    数据库连接类封装
    ~~~~~~~~~~~~~~~~~
"""
import sys
from weberFuncs import PrintTimeMsg

#--------------------------------------
class CDBConnection(object):
    """
        数据库链接类
    """
    def __init__(self, dictEngine, sDbName):
        """
            dictEngine 对应数据库引擎的附加参数，取值示例
            dictEngine = {  # Mysql 数据库引擎的配置
                "engine" : "mysql",     # 数据库引擎类型 mysql sqlite
                "host" : "localhost",   # 主机名
                "port" : 3306,          # 端口号
                # "dbname" : "mysql",   # 库名
                "username" : "mysql",   # 用户名
                "password" : "mysql",   # 密码
                "initcmd" : [           # 初始命令
                    # "set storage_engine=INNODB;",
                    # "SET time_zone = '+8:00';",
                    # "set GLOBAL max_connections=200;",
                    # "set interactive_timeout=24*3600;",
                    "set transaction isolation level read committed;",
                ],
            }
            sDBName = 库名， 若是sqlite的话，不带路径和扩展名部分；独立出来是避免参数重复
        """
        self.oConn = None
        self.oCursor = None
        self.Error = Exception
        self.dictEngine = dictEngine
        self.sEngine = self.dictEngine.get('engine','@ENGINE')
        self.sDbName = sDbName
        self.sConnHint = '%s:%s' % (self.sEngine,self.sDbName)
        PrintTimeMsg("CDBConnection.dictEngine=(%s)" % self.dictEngine)
        # self.dbConnect()

    def __del__(self):
        self.dbClose()

    def __enter__(self):
        # with as 语句入口处理
        # PrintTimeMsg('CDBConnection.__enter__')
        return self #.getConnection()

    def __exit__(self, type, value, traceback):
        # with as 语句出口处理
        # PrintTimeMsg('CDBConnection.__exit__(%s,%s,%s)' % (type, value, traceback))
        self.dbClose()

    def dbConnect(self):
        if self.sEngine=='mysql':
            import MySQLdb
            self.Error = MySQLdb.Error #避免应用层对 MySQLdb 的依赖
            PrintTimeMsg("dbConnect(%s,%s)..." % (self.sEngine,self.sConnHint))
            dbHOST = self.dictEngine.get('host','localhost')
            dbPORT = int(self.dictEngine.get('port',3306))
            dbUSER = self.dictEngine.get('username','mysql')
            dbPASSWD = self.dictEngine.get('password','mysql')
            # sDbName = self.dictEngine.get('dbname','test')
            dbINITCMD  = ''.join(self.dictEngine.get('initcmd',[]))
            self.oConn = MySQLdb.connect(host=dbHOST,port=dbPORT,user=dbUSER,passwd=dbPASSWD,
                                        db=self.sDbName,charset="utf8",init_command=dbINITCMD)
            self.oConn.autocommit(False) # 不自动提交
        else:
            PrintTimeMsg("dbConnect.sEngine=(%s)EXIT!" %(self.sEngine))
            sys.exit(-1)

    def dbClose(self):
        if self.oConn:
            PrintTimeMsg("dbClose(%s,%s)..." % (self.sEngine,self.sConnHint))
            self.oConn.close()
            self.oConn = None
        else:
            PrintTimeMsg("dbClose(%s,%s).oConn=NULL" % (self.sEngine,self.sConnHint))

    def getConnection(self):
        # 获取当前数据库链接
        if (not self.oConn) or (self.oConn.open):
            # PrintTimeMsg("getConnection.oConn is None, need to Connect!")
            self.dbConnect()
        return self.oConn

    def getEngine(self):
        return self.sEngine

    # def sqlCommit(self):
    #     # 提交事务
    #     self.oConn.commit()
    #     # PrintTimeMsg('CDBConnection.sqlCommit()')
    #
    # def sqlRollback(self):
    #     # 回滚事务
    #     self.oConn.rollback()
    #     # PrintTimeMsg('CDBConnection.SqlRollback()')

    def _getErrno(self,e):
        if len(e.args)>=2:
            (errno,errmsg) = e
            return errno
        return -1

    def checkIsInsertEXT(self, e):
        # 判断是否是插入重复
        errno = self._getErrno(e)
        if self.getEngine()=='mysql':
            return errno==1062
        return False

    def checkIsTabCrtEXT(self, e):
        # 判断是否是建表重复
        errno = self._getErrno(e)
        if self.getEngine()=='mysql':
            return errno==1050
        return False

#--------------------------------------

def TestCDBConnection():
    from testDictParam import ReturnMysqlDictParamDB
    c = CDBConnection(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test")
    PrintTimeMsg(c.getConnection())
    # c.SqlExecute('select version()')
# def TestEnum():
#     from enum import Enum
#     class Color(Enum):
#         red, green, blue
#     PrintTimeMsg(Color.red)
#--------------------------------------
if __name__ == '__main__':
    TestCDBConnection()
    # TestEnum()
