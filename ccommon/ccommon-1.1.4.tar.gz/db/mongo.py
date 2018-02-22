#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/22 9:58
# @Author  : chenjw
# @Site    : 
# @File    : mongo.py
# @Software: PyCharm Community Edition
# @Desc    :  pymongo already has it's poolSize

import pymongo
import decimal
import datetime


class Mongo:
    def __init__(self, host, port, dbName, poolSize=8):
        self.host = host
        self.port = port
        self.dbName = dbName
        self.poolSize = poolSize
        self.client = None
        self.db = None

    def connect(self):
        self.client = pymongo.MongoClient(self.host, self.port, connect=False, maxPoolSize=self.poolSize)
        self.db = self.client[self.dbName]

    def close(self):
        if self.client is not None:
            try:
                self.client.close()
            except:
                pass

    def toMap(self, keys, values):
        if len(keys) != len(values):
            raise Exception('len of keys and values is not the same')
        keys = self.toLower(keys)
        ret_map = {}
        for index in range(len(keys)):
            key = keys[index]
            value = values[index]
            if isinstance(value, decimal.Decimal):
                value = float(value)
            if isinstance(value, datetime.datetime):
                value = int(value.timestamp() * 1000)
            ret_map[key] = value
        return ret_map

if __name__ == '__main__':
    pass
