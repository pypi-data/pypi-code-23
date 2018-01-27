# -*- coding: utf-8 -*-
from sqlwriter.writers.base_writer import BaseWriter


class MsSQLWriter(BaseWriter):
    def __init__(self, *args, **kwargs):
        super(MsSQLWriter, self).__init__(*args, **kwargs)

    @property
    def description(self):
        self.curs.execute('SELECT TOP 1 %s FROM %s' % (','.join(self.cols), self.db_table))
        return self.curs.description

    def _make_fields(self):
        import pymssql
        string, datetime, date, numeric, other = [], [], [], [], []
        for i in range(len(self.description)):
            test = self.description[i][1]
            if test == pymssql.STRING.value:
                string.append(i)
            elif test == pymssql.DATETIME.value:
                datetime.append(i)
            elif test == pymssql.DECIMAL.value or test == pymssql.NUMBER.value:
                numeric.append(i)
            else:
                other.append(i)
        return string, datetime, date, numeric, other
