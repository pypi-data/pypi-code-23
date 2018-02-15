# -*- coding: utf-8 -*-

import pymysql.cursors

class Rds():
    def __init__(self, db_host ,db_user ,db_password ,db_name ,charset, debug=False, before_sql=False):
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.charset = charset

        # デバッグモード
        self.debug = debug

        # 実行前のsqlを返す
        self.before_sql = before_sql

    # connectionを返す
    def dbConnection(self):
        if self.debug:
            print('db connection')

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

    # pythonに合わせたsqlのエスケープシーケンスを作成
    def _sqlReplace(self, sql_str):
        return sql_str.replace('"', '\\"')


    # sql実行
    def sqlExecute(self, sql_array):
        cursor_array = []
        for sql in sql_array:
            with self.connection.cursor() as cursor:
                # sql文の実行
                r = cursor.execute(sql)

                # 実行したsql文章
                if self.debug:
                    print(cursor._executed)

                # autocommitではないので、明示的にコミットする
                self.connection.commit()
            cursor_array.append(cursor)
        return cursor_array

    # リストによるインサートの実行
    def insertListExecute(self, table_name ,data_list_array):

        sql_array = []
        for data_list in data_list_array:
            cols = data_list.keys()
            if not isinstance(cols, list):
                cols = list(cols)

            values = data_list.values()
            if not isinstance(values, list):
                values = list(values)

            cols_name = ''
            for col in cols:
                cols_name += col + ','
            cols_name = cols_name[:-1]

            values_name = ''
            for value in values:
                if isinstance(value, int) or isinstance(value, float):
                    values_name += str(value)+ ','
                elif value == 'NULL':
                    values_name += 'NULL ,'
                else:
                    values_name += '"' +self._sqlReplace(value) +'"'+ ','

            values_name = values_name[:-1]

            # sql文の作成
            sql = "INSERT INTO " + table_name + " (" + cols_name + " ) VALUES ( " + values_name + " )"
            sql_array.append(sql)

            # before_sqlがTrueなら一番初めのsqlを返す
            if self.before_sql:
                return sql

        # connection取得、実行
        self.connection = self.dbConnection()
        cursor_array = self.sqlExecute(sql_array)
        self.dbClosed()

        return cursor_array

    # select文実行
    def selectExecute(self, table_name, cols_name, where=''):
        # sql文の作成
        sql = "SELECT " + self._sqlReplace(cols_name) + " FROM " + table_name
        if where :
            sql = sql + " WHERE "+where

        # connection取得、実行
        self.connection = self.dbConnection()
        cursor_array = self.sqlExecute([sql])
        self.dbClosed()

        return cursor_array[0]

    # update文実行
    def updateListExecute(self, table_name, data_list_array, where_word='where'):
        sql_array = []
        for data_list in data_list_array:
            # data_list_arrayにwhereがあればwhereを削除してwhereに代入
            where = ''
            if where_word in data_list:
                where = data_list.pop(where_word)

            cols = data_list.keys()
            if not isinstance(cols, list):
                cols = list(cols)

            values = data_list.values()
            if not isinstance(values, list):
                values = list(values)

            col_value=''
            for i in range(0, len(cols)):
                col_value += cols[i]+'='

                # valueのみ場合分けを行う
                if isinstance(values[i], int) or isinstance(values[i], float):
                    col_value += str(values[i])+ ','
                elif values[i] == 'NULL':
                    col_value += 'NULL ,'
                else:
                    col_value += '"' +self._sqlReplace(values[i]) +'"'+ ','
            col_value = col_value[:-1]

            # sql文の作成
            sql = "UPDATE " + table_name + " SET " + col_value
            if where:
                sql += " WHERE " + where

            # 配列のsql作成
            sql_array.append(sql)

            # before_sqlがTrueなら一番初めのsqlを返す
            if self.before_sql:
                return sql

        # connection取得、実行
        self.connection = self.dbConnection()
        cursor = self.sqlExecute(sql_array)
        self.dbClosed()

        return cursor

    # delete文の実行
    def deleteExecute(self, table_name, where=''):
        # # sql文の実行
        self.connection = self.dbConnection()

        sql = "DELETE FROM " + table_name
        if where :
            sql += " wHERE " + where

        if self.debug:
            print(sql)
        pass



class Tutorial():
    def __init__(self):
        self.rds = Rds(
            )

    def insert(self):
        data = [{'name':'hyu', 'age':21,'favolite':'"aur gunssssssssss"'},{'name':'hyu', 'age':21,'favolite':'"aur guns"'}]
        # self.rds.before_sql = True
        cursor_array = self.rds.insertListExecute('user', data)
        print(cursor_array[0]._executed)
        print(cursor_array[1]._executed)

    def update(self):
        data = [
            {'name':'komeiu', 'age':7, 'favolite':'movies','where':'id=1'},
            {'name':'komeiu', 'age':7, 'favolite':'movies','where':'id=2'},
            {'name':'komeiu', 'age':7, 'favolite':'movies','where':'id=3'}
            ]
        # self.rds.before_sql=True
        cursor_array = self.rds.updateListExecute('user', data)
        print('実行したsql')
        print(cursor_array[0]._executed)
        print(cursor_array[1]._executed)
        print(cursor_array[2]._executed)

        print(cursor_array)

    def select(self):
        cursor = self.rds.selectExecute('user', '*', 'id=4')

        print(cursor.fetchall())
        print(cursor._executed)
        # return cursor._executed
        return cursor

if __name__ == '__main__':
    tutorial = Tutorial()
    r = tutorial.select()
    print(r)









#
