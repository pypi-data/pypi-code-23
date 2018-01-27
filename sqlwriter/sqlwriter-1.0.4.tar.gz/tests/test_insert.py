# -*- coding: utf-8 -*-
import unittest

from utils import DBRouter, create_test_dataframe
from sqlwriter import SQLWriter

class TestInsertMySQL(unittest.TestCase):
    def setUp(self):
        self.df = create_test_dataframe()
        self.db = DBRouter('mysql')

    def test_insert_mysql(self):
        curs, conn = self.db['mysql']
        writer = SQLWriter(conn, 'sqlwriter', 'test', self.df.columns)

        writer.write(self.df.values)
        writer.close()

    def tearDown(self):
        self.db.close()


class TestInsertPostGres(unittest.TestCase):
    def setUp(self):
        self.df = create_test_dataframe()
        self.db = DBRouter('postgres')

    def test_insert_postgres(self):
        curs, conn = self.db['postgres']
        writer = SQLWriter(conn, 'sqlwriter', 'test', self.df.columns)

        writer.write(self.df.values)
        writer.close()

    def tearDown(self):
        self.db.close()

class TestInsertMsSQL(unittest.TestCase):
    def setUp(self):
        self.df = create_test_dataframe()
        self.db = DBRouter('mssql')

    def test_insert_mssql(self):
        curs, conn = self.db['mssql']
        writer = SQLWriter(conn, 'sqlwriter', 'dbo.test', self.df.columns)

        writer.write(self.df.values)
        writer.close()

    def tearDown(self):
        self.db.close()

if __name__ == '__main__':
    unittest.main()
