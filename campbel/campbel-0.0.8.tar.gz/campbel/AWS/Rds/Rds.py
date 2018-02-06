# -*- coding: utf-8 -*-

import pymysql.cursors

class Rds():
    def __init__(self, db_host ,db_user ,db_password ,db_name ,charset, debug=False):
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.charset = charset
        self.connection = self.getConnection()

        # デバッグモード
        self.debug = debug

    # connectionを返す
    def getConnection(self):
        connection = pymysql.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            db=self.db_name,
            charset=self.charset,
            # cursorclassを指定することで
            # Select結果をtupleではなくdictionaryで受け取れ��?
            cursorclass=pymysql.cursors.DictCursor)
        return connection

    # db切断
    def dbClosed(self):
        if self.debug:
            print('db closed')
        self.connection.close()


    # インサートの実行
    def insertExecute(self, table_name, cols_name, values):
        # sql文の作成
        sql = "INSERT INTO " + table_name + " (" + cols_name + " ) VALUES ( " + values + " )"

        if self.debug:
            print(sql)

        # # sql文の実行
        with self.connection.cursor() as cursor:
            r = cursor.execute(sql)

            # autocommitではないので、明示的にコミットする
            self.connection.commit()

        return r

    # リストによるインサートの実行
    def insertListExecute(self, table_name ,data_list_array):

        for data_list in data_list_array:

            cols = data_list.keys()
            values = data_list.values()

            cols_name, values_name = '', ''

            for col in cols:
                cols_name += col + ','
            else:
                cols_name = cols_name[:-1]

            for value in values:
                values_name += str(value) + ','
            else:
                values_name = values_name[:-1]

            # sql文の作成
            sql = "INSERT INTO " + table_name + " (" + cols_name + " ) VALUES ( " + values_name + " )"

            if self.debug:
                print(sql)

            # sql文の実行
            with self.connection.cursor() as cursor:
                r = cursor.execute(sql)

                # autocommitではないので、明示的にコミットする
                self.connection.commit()

        return r



    # select文実行
    def selectExecute(self, table_name, cols_name, where=''):
        # sql文の作成
        sql = "SELECT " + cols_name + " FROM " + table_name
        if where :
            sql = sql + " wHERE "+where

        if self.debug:
            print(sql)

        # SQLを実行する
        with self.connection.cursor() as cursor:
            cursor.execute(sql)

            # Select結果を取り出す
            results = cursor.fetchall()

        return results

    # update文実行
    def updateExecute(self, table_name, col_value, where=''):
        # sql文の作成
        sql = "UPDATE " + table_name + " SET " + col_value
        if where :
            sql += " WHERE " + where

        if self.debug:
            print(sql)

        # # sql文の実行
        with self.connection.cursor() as cursor:
            r = cursor.execute(sql)

            # autocommitではないので、明示的にコミットする
            self.connection.commit()

        return r


    # update文実行
    def updateListExecute(self, table_name, data_list_array, where_array=''):
        count = 0
        for j in range(0, len(data_list_array)):
            col_value=''

            cols = data_list_array[j].keys()
            values = data_list_array[j].values()

            for i in range(0, len(cols)):
                col_value += cols[i]+'='+str(values[i])+','
            col_value = col_value[:-1]

            # sql文の作成
            sql = "UPDATE " + table_name + " SET " + col_value
            if where_array:
                sql += " WHERE " + where_array[j]

            if self.debug:
                print(sql)

            # # sql文の実行
            with self.connection.cursor() as cursor:
                r = cursor.execute(sql)

                # autocommitではないので、明示的にコミットする
                self.connection.commit()

            count += 1

        return r


    # delete文の実行
    def deleteExecute(self, table_name, where=''):
        sql = "DELETE FROM " + table_name
        if where :
            sql += " wHERE " + where

        if self.debug:
            print(sql)








        pass










#
