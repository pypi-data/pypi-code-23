# -*- coding: utf-8 -*-
import unittest

from utils import DBRouter


class TestCreatePostgres(unittest.TestCase):
    def setUp(self):
        self.db = DBRouter('postgres')

    def test_create_table(self):
        curs, conn = self.db['postgres']
        curs.execute('DROP TABLE IF EXISTS test')
        conn.commit()
        sql = '''
        CREATE TABLE test (
            id SERIAL
            , astring VARCHAR(50)
            , aninteger INTEGER
            , afloat FLOAT
            , adate DATE
            , adatetime TIMESTAMP WITHOUT TIME ZONE
        )
        '''
        curs.execute(sql)
        conn.commit()

    def tearDown(self):
        self.db.close()


class TestCreateMySQL(unittest.TestCase):
    def setUp(self):
        self.db = DBRouter('mysql')

    def test_create_dbmysql(self):
        curs, conn = self.db['mysql']
        curs.execute('CREATE DATABASE IF NOT EXISTS sqlwriter')
        conn.commit()

    def test_create_tablemysql(self):
        curs, conn = self.db['mysql']
        curs.execute('DROP TABLE IF EXISTS sqlwriter.test')
        conn.commit()
        sql = '''
        CREATE TABLE test (
            id SERIAL
            , astring VARCHAR(50)
            , aninteger INTEGER
            , afloat FLOAT
            , adate DATE
            , adatetime DATETIME
        )
        '''
        curs.execute(sql)
        conn.commit()

    def tearDown(self):
        self.db.close()


class TestCreateMsSQL(unittest.TestCase):
    def setUp(self):
        self.db = DBRouter('mssql')

    def test_create_dbmssql(self):
        _, conn = self.db['mssql']
        conn.autocommit(True)
        curs = conn.cursor()
        curs.execute("IF EXISTS(select * from sys.databases where name='sqlwriter') DROP DATABASE sqlwriter")
        conn.commit()

        curs.execute('CREATE DATABASE sqlwriter')
        conn.commit()

    def test_create_tablemssql(self):
        curs, conn = self.db['mssql']
        curs.execute("IF OBJECT_ID('sqlwriter.dbo.test') IS NOT NULL DROP TABLE sqlwriter.dbo.test")
        conn.commit()
        sql = '''
        CREATE TABLE sqlwriter.dbo.test (
            id INT IDENTITY(1,1)
            , astring NVARCHAR(50)
            , aninteger INT
            , afloat FLOAT
            , adate DATE
            , adatetime DATETIME
        )
        '''
        curs.execute(sql)
        conn.commit()

    def tearDown(self):
        self.db.close()


if __name__ == '__main__':
    unittest.main()
