# -*- coding: utf-8 -*-

from pandas import DataFrame
from sqlwriter import SQLWriter


class SQLDataFrame(DataFrame):
    def __init__(self, *args, **kwargs):
        DataFrame.__init__(self, *args, **kwargs)

    def to_sql(self, conn, database, tablename, write_limit=200, truncate=False):
        writer = SQLWriter(conn, database, tablename, self.columns, write_limit, truncate)
        writer.write(self.values)
        writer.close()
