#!/usr/bin/env python
# -*- coding: utf8 -*-

import MySQLdb
from gorgou.x import jsonx


class Connection(object):
    # BASIC

    def __init__(self, mysql_conf_file=None):
        if not mysql_conf_file:
            mysql_conf_file = 'mysql.conf'
        mysql_conf = jsonx.load_json(mysql_conf_file)
        self.connection = MySQLdb.connect(
            host=mysql_conf['host'],
            user=mysql_conf['user'],
            passwd=mysql_conf['passwd'],
            db=mysql_conf['db'],
            port=mysql_conf['port'],
            charset='utf8'
        )
        self.cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)

    @property
    def cur(self):
        return self.cursor

    @cur.setter
    def cur(self, value):
        self.cursor = value

    @property
    def conn(self):
        return self.connection

    @conn.setter
    def conn(self, value):
        self.connection = value

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def execute(self, *args, **kwargs):
        return self.cur.execute(*args, **kwargs)

    def close(self):
        self.cur.close()
        self.conn.close()

    # ADVANCED
    def get(self, *args, **kwargs):
        self.cur.execute(*args, **kwargs)
        return self.cur.fetchall()

    def get_one(self, *args, **kwargs):
        self.cur.execute(*args, **kwargs)
        return self.cur.fetchone()

    def get_page(self, table, orderBy, where, pageSize, pageNum):
        pager = {}
        pager['pageSize'] = pageSize
        pager['pageNum'] = pageNum
        l = pager['pageSize']
        o = (pager['pageNum'] - 1) * pager['pageSize']
        tmpsql = 'select count(*) as count from ' + table
        if where:
            tmpsql = tmpsql + ' where ' + where
        count = self.get_one(tmpsql)['count']
        pager['pageCount'] = int(
            (count + pager['pageSize'] - 1) / pager['pageSize'])
        if not pager['pageCount']:
            pager['pageCount'] = 1
        tmpsql = 'select * from ' + table
        if where:
            tmpsql = tmpsql + ' where ' + where
        if not orderBy:
            # error
            pass
        tmpsql = tmpsql + ' order by ' + orderBy + ' limit %s offset %s'
        result = self.get(tmpsql, (l, o,))
        return result, pager

    def safe_execute(self, *args, **kwargs):
        try:
            self.cur.execute(*args, **kwargs)
            self.conn.commit()
        except:
            self.conn.rollback()

    def safe_execute_ret_rowcount(self, *args, **kwargs):
        try:
            self.cur.execute(*args, **kwargs)
            self.conn.commit()
            return self.cur.rowcount
        except:
            self.conn.rollback()
            return 0

    def safe_execute_ret_lastrowid(self, *args, **kwargs):
        try:
            self.cur.execute(*args, **kwargs)
            self.conn.commit()
            return self.cur.lastrowid
        except:
            self.conn.rollback()
            return 0
