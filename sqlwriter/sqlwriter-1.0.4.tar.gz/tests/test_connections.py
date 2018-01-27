# -*- coding: utf-8 -*-
import subprocess as sp
import unittest

from utils import connect_db

p = sp.Popen('docker ps', shell=True, stdout=sp.PIPE)
p.wait()
msg, _ = p.communicate()

SKIP_MYSQL = True
SKIP_POSTGRES = True
SKIP_MSSQL = True

if 'sqlwriter_postgres_1' in msg:
    SKIP_POSTGRES = False
if 'sqlwriter_mysql_1' in msg:
    SKIP_MYSQL = False
if 'sqlwriter_mssql_1' in msg:
    SKIP_MSSQL = False


class TestDBConnections(unittest.TestCase):

    @unittest.skipIf(SKIP_MYSQL, 'Could not find running MySQL docker container')
    def test_mysql_can_connect(self):
        try:
            curs, conn = connect_db('mysql')
            self.assertTrue(True)
            curs.close()
            conn.close()
        except Exception as e:
            print(e)
            self.assertTrue(False)

    @unittest.skipIf(SKIP_POSTGRES, 'Could not find running Postgres docker container')
    def test_postgres_can_connect(self):
        try:
            curs, conn = connect_db('postgres')
            self.assertTrue(True)
            curs.close()
            conn.close()
        except Exception as e:
            print(e)
            self.assertTrue(False)

    @unittest.skipIf(SKIP_MSSQL, 'Could not find running MsSQL docker container')
    def test_mssql_can_connect(self):
        try:
            curs, conn = connect_db('mssql')
            self.assertTrue(True)
            curs.close()
            conn.close()
        except Exception as e:
            print(e)
            self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
