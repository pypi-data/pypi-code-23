# coding: utf-8

from tornado import gen
import datetime
from miceshare.util import vars
import pandas as pd

# log = logger.logger
POOL = None

'''
dao操作基类，用于统一操作
'''
class dao_base(object):

    is_dev = True

    if is_dev:
        dbconfig = dict(
            database='smart_stock',
            user='stock',
            password='1234567',
            host='127.0.0.1',
            port=3306,
            charset="utf8"
        )
    else:
        dbconfig = dict(
            database='antman_stock',
            user='antman',
            password='7SZqMjEbrQ7WvNU8',
            host='rm-wz9768lm302k078o7.mysql.rds.aliyuncs.com',
            port=3306,
            charset="utf8"
        )

    def _get_conn(self):
        global POOL
        if POOL is None:
            print("init database pool")
            import mysql.connector.pooling
            POOL = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **self.dbconfig)
            print("init db successed")
        con = POOL.get_connection()
        return con

    def _close_conn(self, conn):
        conn.close()

    def excute(self,query,params):
        con = self._get_conn()
        try:
            c = con.cursor()
            c.execute(query, params)
            con.commit()
            rows_affected = c.rowcount
            c.close()
            return rows_affected
        finally:
            con.close()

    def query(self, query, params):
        print(query,params)
        conn = self._get_conn()
        list = []
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            for row in cur:
                # log.info([row[0], row[1]])
                list.append(row)
            cur.close()
        finally:
            conn.close()

        return list

    #插入一行
    def insert_row(self,query,params):
        return self.excute(query,params)

    #判断是否存在
    def exist(self,query,params):
        count = self.count(query,params)
        return count>0

    def count(self,query, params):
        con = self._get_conn()
        count = 0
        try:
            c = con.cursor()
            c.execute(query, params)
            # rows_affected = c.rowcount
            count = c.fetchone()[0]
        finally:
            con.close()
        return count

    def delete(self, query, params):
        self.excute(query, params)


class stock_dao(dao_base):

    def __init__(self):
        # print("init stock")
        super(stock_dao,self).__init__()
        self.name='stock'

    def insert(self,code,name,date,ex):
        query = "INSERT INTO stock(code,name,time,exchange) VALUE (%s,%s,%s,%s)"
        params = [code,name,date,ex]
        if self.is_exist(code):
            return 0
        return self.insert_row(query,params)

    def is_exist(self,code):
        query = "select count(code) from stock where code=%s"
        params = [code]
        is_exist = self.exist(query, params)
        return is_exist

    def select(self,time):
        query = "select code,name,time,exchange from stock where time<=%s"
        params = [time]
        return self.query(query,params)


class board_dao(dao_base):

    def __init__(self):
        # print("init stock")
        super(board_dao,self).__init__()
        self.name='board'

    def insert(self,code,name,type,channel):
        query = "INSERT INTO board(code,name,type,channel) VALUE (%s,%s,%s,%s)"
        params = [code,name,type,channel]
        if self.is_exist(code):
            return 0
        return self.insert_row(query,params)

    def is_exist(self,code):
        query = "select count(code) from board where code=%s"
        params = [code]
        is_exist = self.exist(query, params)
        return is_exist

    def select(self):
        query = "select code,name,type,channel from board"
        params = None
        return self.query(query,params)

class board_stock_dao(dao_base):

    def __init__(self):
        # print("init stock")
        super(board_stock_dao,self).__init__()
        self.name='board_stock'

    def insert(self,stock_code,board_code):
        query = "INSERT INTO board_stock(stock_code,board_code) VALUE (%s,%s)"
        params = [stock_code,board_code]
        if self.is_exist(stock_code,board_code):
            return 0
        return self.insert_row(query,params)

    def is_exist(self,stock_code,board_code):
        query = "select count(stock_code) from board_stock where stock_code=%s and board_code=%s"
        params = [stock_code,board_code]
        is_exist = self.exist(query, params)
        return is_exist

    def select(self):
        query = "select stock_code,board_code from board_stock"
        params = None
        return self.query(query,params)

    def query_stocks_by_board(self,board_name,board_type=vars.Board_C,channel=1):
        query = "select A.stock_code from board_stock A LEFT JOIN board B on A.board_code=B.code WHERE B.name=%s and B.type=%s and B.channel=%s"
        params = [board_name,board_type,channel]
        l = self.query(query, params)
        return pd.DataFrame(l, columns=['stock_code'])['stock_code'].values



stock_dao = stock_dao()
board_dao = board_dao()
board_stock_dao = board_stock_dao()

if __name__ == '__main__':
    s = board_stock_dao.query_stocks_by_board('基金重仓',vars.Board_C,0)
    print(s)
# print(stock_dao.is_exist(123))
# stock_dao.insert(12346,'abc','2017-09-09','sh')
# stock_dao.insert(12345,'abc','2017-09-09','sh')
# print(stock_dao.select('2017-09-09'))