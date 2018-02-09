# -*- coding: utf-8 -*-

import pymysql.cursors

class Rds():
    def __init__(self, db_host ,db_user ,db_password ,db_name ,charset, debug=False):
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.charset = charset

        # デバッグモード
        self.debug = debug

    # connectionを返す
    def _dbConnection(self):
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

    # sql実行
    def sqlExecute(self, sql):
        # # sql文の実行
        self.connection = self._dbConnection()
        with self.connection.cursor() as cursor:
            r = cursor.execute(sql)

            # 実行したsql文章
            if self.debug:
                print(cursor._executed)

            # autocommitではないので、明示的にコミットする
            self.connection.commit()


        return cursor

    # # インサートの実行
    # def insertExecute(self, table_name, cols_name, values):
    #     # sql文の作成
    #     sql = "INSERT INTO " + table_name + " (" + cols_name + " ) VALUES ( " + values + " )"
    #
    #     # sqlの実行
    #     r = self.sqlExecute(sql)
    #
    #     self.dbClosed()
    #     return r

    # リストによるインサートの実行
    def insertListExecute(self, table_name ,data_list_array):
        for data_list in data_list_array:
            cols = data_list.keys()
            if not isinstance(cols, list):
                cols = list(cols)

            values = data_list.values()
            if not isinstance(values, list):
                values = list(values)

            cols_name, values_name = '', ''
            for col in cols:
                cols_name += col + ','
            cols_name = cols_name[:-1]

            for value in values:
                if isinstance(value, int) or isinstance(value, float):
                    print(1)
                    values_name += str(value)+ ','
                elif value == 'NULL':
                    print(2)
                    values_name += value+ ','
                else:
                    print(3)
                    values_name += '"' +value +'"'+ ','

            values_name = values_name[:-1]

            # sql文の作成
            sql = "INSERT INTO " + table_name + " (" + cols_name + " ) VALUES ( " + values_name + " )"

            # sqlの実行
            cursor = self.sqlExecute(sql)

        self.dbClosed()
        return cursor

    # select文実行
    def selectExecute(self, table_name, cols_name, where=''):
        # sql文の作成
        sql = "SELECT " + cols_name + " FROM " + table_name
        if where :
            sql = sql + " WHERE "+where

        # sqlの実行
        # Select結果を取り出す
        cursor = self.sqlExecute(sql)

        self.dbClosed()
        return cursor

    # # update文実行
    # def updateExecute(self, table_name, col_value, where=''):
    #     # sql文の作成
    #     sql = "UPDATE " + table_name + " SET " + col_value
    #     if where :
    #         sql += " WHERE " + where
    #
    #     # sqlの実行
    #     r = self.sqlExecute(sql)
    #
    #     self.dbClosed()
    #     return r

    # update文実行
    def updateListExecute(self, table_name, data_list_array, where_word='where'):
        for data_list in data_list_array:
            # data_list_arrayにwhereがあればwhereを削除してwhereに代入
            where = ''
            if where_word in data_list:
                where = data_list.pop(where_word)
            print(data_list)

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
                    print(1)
                    col_value += str(values[i])+ ','
                elif values[i] == 'NULL':
                    print(2)
                    col_value += values[i]+ ','
                else:
                    print(3)
                    col_value += '"' +values[i] +'"'+ ','
            col_value = col_value[:-1]

            # sql文の作成
            sql = "UPDATE " + table_name + " SET " + col_value
            if where:
                sql += " WHERE " + where

            # sqlの実行
            cursor = self.sqlExecute(sql)

        self.dbClosed()
        return cursor

    # delete文の実行
    def deleteExecute(self, table_name, where=''):
        sql = "DELETE FROM " + table_name
        if where :
            sql += " wHERE " + where

        if self.debug:
            print(sql)








        pass



class Tutorial():
    def __init__(self):
        self.rds = Rds(
            db_host = '',
            db_user = '',
            db_password = '',
            db_name = '',
            charset = 'utf8',
            debug=False
            )


    def insert(self):
        data = [{'name':'hyu', 'age':21,'favolite':'aur guns'}]
        cursor = self.rds.insertListExecute('user', data)
        print(cursor)

    def update(self):
        data = [{'name':'komei', 'age':7, 'favolite':'movies','where':'id=5'}]
        cursor = self.rds.updateListExecute('user', data)
        print(cursor)

    def select(self):
        cursor = self.rds.selectExecute('user', '*', '')
        return cursor._executed

if __name__ == '__main__':
    tutorial = Tutorial()
    print(tutorial.select())









#
