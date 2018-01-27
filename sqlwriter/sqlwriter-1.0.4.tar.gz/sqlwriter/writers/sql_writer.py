# -*- coding: utf-8 -*-
from sqlwriter.writers.mssql_writer import MsSQLWriter
from sqlwriter.writers.mysql_writer import MySQLWriter
from sqlwriter.writers.postgres_writer import PostGresWriter


class SQLWriter(object):
    '''
    Wrapper class for implementing one flavor of sql writer. There may be a more
    pythonic/ inheritance method of doing this.
    '''
    def __init__(self, conn, *args, **kwargs):
        self.conn = conn
        if self.flavor == 'mssql':
            self.impl = MsSQLWriter(conn, *args, **kwargs)
        elif self.flavor == 'mysql':
            self.impl = MySQLWriter(conn, *args, **kwargs)
        elif self.flavor == 'postgres':
            self.impl = PostGresWriter(conn, *args, **kwargs)

    @property
    def flavor(self):
        flavors = {
            'MySQLdb': 'mysql',
            'psycopg2': 'postgres',
            'cx_Oracle': 'oracle',
            'pymssql': 'mssql'
        }
        module = self.conn.__class__.__module__
        if '.' in module:
            module = module.split('.')[0]
        return flavors[module]

    def write(self, *args):
        self.impl.write(*args)

    def close(self):
        self.impl.close()
