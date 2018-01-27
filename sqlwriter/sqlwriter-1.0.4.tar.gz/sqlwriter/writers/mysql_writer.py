# -*- coding: utf-8 -*-
from sqlwriter.writers.base_writer import BaseWriter


class MySQLWriter(BaseWriter):
    def __init__(self, *args, **kwargs):
        super(MySQLWriter, self).__init__(*args, **kwargs)

    @property
    def description(self):
        self.curs.execute('SELECT %s FROM %s LIMIT 1' % (','.join(self.cols), self.db_table))
        return self.curs.description

    def _make_fields(self):
        import MySQLdb
        # TODO: may have to expand this to include blobs under string, etc.
        string, datetime, date, numeric, other = [], [], [], [], []
        for i in range(len(self.description)):
            test = self.description[i][1]
            if test == MySQLdb.STRING:
                string.append(i)
            elif test == MySQLdb.TIMESTAMP or test == MySQLdb.TIME:
                datetime.append(i)
            elif test == MySQLdb.NUMBER:
                numeric.append(i)
            elif test == MySQLdb.DATE:
                date.append(i)
            else:
                other.append(i)
        return string, datetime, date, numeric, other
