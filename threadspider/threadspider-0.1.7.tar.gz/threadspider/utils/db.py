#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2017/1/17.
# ---------------------------------
import  MySQLdb



class MySQLMgr(object):
    def __init__(self, host, port, db, user, passwd):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.passwd = passwd

    def runQuery(self, sql, args):
        if ("select" not in sql) and ("SELECT" not in sql):
            return ()
        else:
            conn = MySQLdb.connect(host=self.host, port=self.port, db=self.db, user=self.user, passwd=self.passwd,
                                   charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql, args)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result

    def runOperation(self, sql, args, withpaimarykey=False):
        conn = MySQLdb.connect(host=self.host, port=self.port, db=self.db, user=self.user, passwd=self.passwd,
                               charset="utf8")
        cursor = conn.cursor()
        rows = cursor.execute(sql, args)
        conn.commit()
        cursor.close()
        conn.close()
        if withpaimarykey == True:
            return int(rows), int(cursor.lastrowid)
        else:
            return int(rows)