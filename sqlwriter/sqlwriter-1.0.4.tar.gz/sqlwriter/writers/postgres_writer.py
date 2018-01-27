# -*- coding: utf-8 -*-
from sqlwriter.writers.base_writer import BaseWriter


class PostGresWriter(BaseWriter):
    def __init__(self, *args, **kwargs):
        super(PostGresWriter, self).__init__(*args, **kwargs)

    @property
    def insert_part(self):
        return 'INSERT INTO {} ('.format(self.table_name) + ','.join(self.cols) + ') VALUES '

    @property
    def description(self):
        self.curs.execute('SELECT %s FROM %s LIMIT 1' % (','.join(self.cols), self.table_name))
        return self.curs.description

    def _make_fields(self):
        import psycopg2
        string, datetime, date, numeric, other = [], [], [], [], []
        for i in range(len(self.description)):
            test = self.description[i][1]
            if test in psycopg2.STRING.values:
                string.append(i)
            elif test in psycopg2.DATETIME.values:
                datetime.append(i)
            elif test in psycopg2.NUMBER.values:
                numeric.append(i)
            elif test in (1082,):
                date.append(i)
            else:
                other.append(i)
        return string, datetime, date, numeric, other
