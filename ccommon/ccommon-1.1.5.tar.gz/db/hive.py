#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/22 10:14
# @Author  : chenjw
# @Site    : 
# @File    : hive.py
# @Software: PyCharm Community Edition
# @Desc    :  without poolsize

from impala.dbapi import connect as hive_connect


class Hive:
    def __init__(self, host, port, user, password, database, auth_mechanism):
        self.host = host
        self.port = port
        self.database = database
        self.auth_mechanism = auth_mechanism
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        self.conn = hive_connect(host=self.host,
                                 port=self.port,
                                 user=self.user,
                                 password=self.password,
                                 kerberos_service_name='test',
                                 database=self.database,
                                 auth_mechanism=self.auth_mechanism)

    def getConn(self):
        if self.conn is None:
            self.connect()
        return self.conn

    def ExecQuery(self, hql):
        with self.getConn().cursor() as cursor:
            cursor.execute(hql)
            result = cursor.fetchall()
            return result

    def close(self):
        if self.conn is not None:
            try:
                self.conn.close()
            except:
                pass


if __name__ == '__main__':
    pass
