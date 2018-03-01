#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/22 9:49
# @Author  : chenjw
# @Site    : 
# @File    : mysql.py
# @Software: PyCharm Community Edition
# @Desc    :  pymysql need to rely on PooledDB

import pymysql
from DBUtils.PooledDB import PooledDB


class Mysql:
    def __init__(self, host, port, user, pwd, db, poolSize=8):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self.poolSize = poolSize
        self.pool = None

    def connect(self):
        self.pool = PooledDB(pymysql, host=self.host, user=self.user, passwd=self.pwd, db=self.db,
                             port=self.port, charset="utf8", maxconnections=self.poolSize, maxcached=self.poolSize,
                             mincached=self.poolSize)

    def getPool(self):
        if self.pool is None:
            self.connect()
        return self.pool

    def close(self):
        if self.pool is not None:
            try:
                self.pool.close()
            except:
                pass

    def insert(self, sqls):
        '''
        :param sqls: list
        :return:
        '''
        try:
            conn = self.getPool().connection()
            cur = conn.cursor()
            for sql in sqls:
                cur.execute(sql)
            conn.commit()
            return None
        except Exception as e:
            raise Exception(e)
        finally:
            try:
                cur.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass

    def excute(self, sql, ret=True, commit=False):
        '''
        :param sql: Str
        :param ret: ret or not
        :param commit: call commit or not
        :return:
        '''
        try:
            conn = self.getPool().connection()
            cur = conn.cursor()
            cur.execute(sql)
            if commit:
                conn.commit()
            r = None
            if ret:
                r = cur.fetchall()
            return r
        except Exception as e:
            raise Exception(e)
        finally:
            try:
                cur.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass

    def showCreateTable(self, table):
        '''
        :param table: table name
        :return: str of create table
        '''
        sql = 'show create table %s' % table
        create = ''
        for cell in self.ary2D(self.excute(sql))[0][1:]:
            create += cell + '\n'
        return create

    def showTables(self):
        '''

        :return: ary 1D
        '''
        sql = 'show tables'
        return self.ary1D(self.excute(sql))

    def showField(self, table):
        sql = 'desc %s' % table
        return self.ary1D(self.excute(sql))

    def dropTable(self, table):
        sql = 'drop table %s' % table
        self.excute(sql, False)

    def join(self, fields, sep=','):
        '''
        :param fields: ary of field
        :param sep: default ,
        :return: str like field1,field2
        '''
        ret = sep.join(fields)
        return ret

    def count(self, table):
        sql = 'select count(*) from %s' % table
        return self.ary1D(self.excute(sql))[0]

    def ary1D(self, rsp):
        ret = []
        if rsp is None:
            pass
        else:
            for sin_tuple in rsp:
                if len(sin_tuple) > 0:
                    ret.append(sin_tuple[0])
        return ret

    def ary2D(self, rsp):
        ret = []
        if rsp is None:
            pass
        else:
            for sin_tuple in rsp:
                ary_tmp = []
                for sin in sin_tuple:
                    ary_tmp.append(sin)
                ret.append(ary_tmp)
        return ret


if __name__ == '__main__':
    pass
