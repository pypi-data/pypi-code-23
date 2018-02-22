#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/22 10:03
# @Author  : chenjw
# @Site    : 
# @File    : redisdb.py
# @Software: PyCharm Community Edition
# @Desc    :  do what

import redis


class Redis:
    def __init__(self, host, port, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.pool = None

    def connection(self):
        self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password)

    def getRedis(self):
        if self.pool is None:
            self.connection()
        return redis.Redis(connection_pool=self.pool)

    def push(self, key, infos):
        r = self.getRedis()
        for info in infos:
            r.lpush(key, info)

    def pop(self, key):
        return self.getRedis().rpop(key)


if __name__ == '__main__':
    pass
