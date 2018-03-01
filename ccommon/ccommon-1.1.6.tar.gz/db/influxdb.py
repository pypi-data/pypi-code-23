#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/21 13:52
# @Author  : chenjw
# @Site    : 
# @File    : influxdb.py
# @Software: PyCharm Community Edition
# @Desc    :  do what

from influxdb import InfluxDBClient
import logging


class InfluxDB:
    def __init__(self, host, port, username, pwd, database):
        self.host = host
        self.port = port
        self.username = username
        self.pwd = pwd
        self.database = database
        self.client = None

    def getClient(self):
        if self.client is None:
            self.connect()
        return self.client

    def connect(self):
        self.client = InfluxDBClient(self.host, self.port, self.username, self.pwd, self.database)
        self.client.create_database(self.database)

    def close(self):
        try:
            self.client.close()
        except:
            pass

    def query_one(self, value='value', measurement='measurement', where=[]):
        '''
        :param value: key of fields
        :param measurement: measurement
        :param where: conditions
        :return: value of None
        '''
        _query = 'select %s from %s' % (value, measurement)
        if len(where) > 0:
            def combine_where(ss):
                if len(ss) == 1:
                    return ' where ' + ss
                else:
                    tmp = ''
                    for index in range(len(ss)):
                        if index == len(ss) - 1:
                            tmp += ss[index]
                        else:
                            tmp += ss[index] + ' and '
                    return ' where ' + tmp

            _query += combine_where(where)
        _query += ' limit 1'
        result = self.getClient().query(_query)
        try:
            for tmp in result[result.keys()[0]]:
                return tmp[value]
        except:
            return None
        return None

    def recordinfo(self, measurement, date, _time, fields, tags={}):
        '''
        :param client: influxdb client
        :param measurement: key to measure a series of data
        :param date: date like '2018-01-01'
        :param fields:  common like {'value':12.34}
        :param tags: like {'a':'a','b':'b'} use tags to group by data
        :return: nothing ,sometimes print msg if raise Exception
        '''
        try:
            if date is not None:
                self.getClient().write_points([
                    {
                        "measurement": measurement,
                        "tags": tags,
                        "time": "%sT01:00:00Z" % date,
                        "fields": fields
                    }
                ])
            else:
                self.getClient().write_points([
                    {
                        "measurement": measurement,
                        "tags": tags,
                        "time": "%s" % _time,
                        "fields": fields
                    }
                ])
        except Exception as e:
            logging.error('call recordinfo raise exception %s' % e)


if __name__ == '__main__':
    i = InfluxDB('192.168.38.187', 8086, '', '', 'recommend')
    print(i.query_one())
    pass
