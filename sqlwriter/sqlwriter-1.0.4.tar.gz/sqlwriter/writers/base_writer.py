# -*- coding: utf-8 -*-
import pandas as pd
from dateutil import parser
from sqlwriter.utils.utils import chunks
from unidecode import unidecode


class BaseWriter(object):
    '''
    Base writer object performs mogifying and inserting.
    '''
    def __init__(self,
                 conn,
                 database,
                 table_name,
                 cols,
                 write_limit=200,
                 truncate=False):
        self.conn = conn
        self.curs = conn.cursor()
        self.database = database
        self.table_name = table_name
        self.cols = cols
        self.write_limit = write_limit
        self._truncate = truncate

        self.fields = self._fields_to_dict()

    @property
    def insert_part(self):
        '''
        Generic insert statement. Some writers will override this
        '''
        return 'INSERT INTO {} ('.format(self.db_table) + ','.join(self.cols) + ') VALUES '

    @property
    def flavor(self):
        flavor_map = {
            'MySQLdb': 'mysql',
            'psycopg2': 'postgres',
            'cx_Oracle': 'oracle',
            'pymssql': 'mssql'
        }
        module = self.conn.__class__.__module__
        if '.' in module:
            module = module.split('.')[0]
        return flavor_map[module]

    @property
    def db_table(self):
        '''
        Generic db table string. Some writers will override this.
        '''
        return '.'.join([self.database, self.table_name])

    @property
    def description(self):
        '''
        Because select 1 syntax varies, writer will implement this
        '''
        raise NotImplementedError()

    def _fields_to_dict(self):
        '''
        Returns a dictionary of fields based on sql connections package's data
        types
        '''
        keys = ('string', 'datetime', 'date', 'numeric', 'other')
        values = self._make_fields()
        return dict(zip(keys, values))

    def _make_fields(self):
        '''
        Must be implemented for each connection module
        '''
        raise NotImplementedError()

    def _mogrify(self, row):
        """String formats data based on fields to be able to multi-insert into
        MySQL

        Parameters
        ---------
        row : array-like
            An array of data to be written to the columns in the target table

        Returns
        -------
        string:
            row formatted as string tuple for easy mysql writing
        """
        if isinstance(row, tuple):
            row = list(row)  # needs to be mutable
        for idx in self.fields['string']:
            try:
                row[idx] = "'{}'".format(str(row[idx]).replace("'", "")) if row[idx] else 'NULL'
            except UnicodeEncodeError:
                row[idx] = "'{}'".format(unidecode(row[idx])) if row[idx] else 'NULL'

        for idx in self.fields['datetime']:
            try:
                row[idx] = row[idx].strftime("'%Y-%m-%d %H:%M:%S'") if row[idx] else 'NULL'
            except AttributeError:
                row[idx] = parser.parse(row[idx])
                row[idx] = row[idx].strftime("'%Y-%m-%d %H:%M:%S'")
            except:
                row[idx] = 'NULL'

        for idx in self.fields['date']:
            row[idx] = row[idx].strftime("'%Y-%m-%d'") if row[idx] else 'NULL'

        for idx in self.fields['numeric']:
            if row[idx] == '':
                row[idx] = 'NULL'
            else:
                row[idx] = str(row[idx])

        for idx in self.fields['other']:
            row[idx] = str(row[idx]) if row[idx] else 'NULL'

        return '(%s)' % ','.join(row)

    def truncate(self):
        '''
        Truncates the table
        '''
        # NOTE: I'm pretty sure this syntax is universal
        if self._truncate:
            self.curs.execute('TRUNCATE TABLE {}'.format(self.db_table))
            self.conn.commit()

    def write(self, rows):
        """Truncates table, formats strings in data and multi-inserts into MySQL

        Parameters
        ----------
        rows: array-like
            An array of arrays of data to be written to the target table
        """
        if isinstance(rows, pd.DataFrame):
            rows = rows.values

        self.truncate()
        if len(rows) == 0:
            return
        queries = chunks(rows, self.write_limit)
        for query in queries:
            query = [self._mogrify(x) for x in query]

            self.curs.execute(self.insert_part + ','.join(query))
            self.conn.commit()

    def close(self):
        self.curs.close()
        self.conn.close()
