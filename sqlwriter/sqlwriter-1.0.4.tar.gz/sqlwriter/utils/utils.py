# -*- coding: utf-8 -*-
'''
Created Friday August 1, 2017
Purpose: utility functions that Sebastian finds useful
@author: sestenssoro
'''
import datetime as dt
import logging
import logging.handlers
import os
import re
import sys

import pandas as pd

header = '''
   _____ ____    __ _       __     _ __
  / ___// __ \  / /| |     / /____(_) /____  _____
  \__ \/ / / / / / | | /| / / ___/ / __/ _ \/ ___/
 ___/ / /_/ / / /__| |/ |/ / /  / / /_/  __/ /
/____/\___\_\/_____/__/|__/_/  /_/\__/\___/_/

'''

data_tests = [
    ('int', int),
    ('float', float),
    ('datetime', lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')),
    ('datetime', lambda x: dt.datetime.strptime(x, '%Y/%m/%d %H:%M:%S')),
    ('date', lambda x: dt.datetime.strptime(x, '%Y-%m-%d')),
    ('date', lambda x: dt.datetime.strptime(x, '%Y/%m/%d')),
]


def detect_data_type(value):
    for typ, test in data_tests:
        try:
            test(value)
            return typ
        except:
            continue
    return 'string'


def chunks(l, n):
    """Generator that splits a list into equal peices of length n

    Parameters
    ----------
    l: Array-like
        Array to be split
    n: Integer
        Length of each sub array
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


class MyLogger(object):
    """Logging object

    Parameters
    ----------
    prog: String
        name of program that is being logged
    to_console: Boolean, default True
        log to console

    Returns
    -------
    logger : Python logging object
    """

    def __init__(self, prog=None, to_console=True):
        if prog is None:
            prog = os.path.basename(sys.argv[0])
            if prog.endswith('.py'):
                prog = prog[:-3]

        self.my_logger = logging.getLogger(prog)
        if os.path.exists('log'):
            LOG_DIR = 'log'
        else:
            wd = os.getcwd()
            while True:
                pardir = os.path.abspath(os.path.join(wd, os.pardir))
                if pardir == wd:
                    LOG_DIR = None
                    break
                if os.path.exists(os.path.join(pardir, 'log')):
                    LOG_DIR = os.path.join(pardir, 'log')
                    break
                wd = pardir

        if LOG_DIR:
            LOG_FILENAME = os.path.join(LOG_DIR, prog + '.log')
        else:
            LOG_FILENAME = prog + '.log'

        self.my_logger.setLevel(logging.DEBUG)
        self.log_filename = LOG_FILENAME
        self.handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5 * 1024 * 1024, backupCount=15)
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.handler.setFormatter(self.formatter)
        self.handler.setLevel(logging.DEBUG)
        self.my_logger.addHandler(self.handler)

        if to_console:
            self.consolehandler = logging.StreamHandler()
            self.consolehandler.setLevel(logging.INFO)
            self.consoleformatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            self.consolehandler.setFormatter(self.consoleformatter)
            self.my_logger.addHandler(self.consolehandler)

    def getLogger(self):
        return self.my_logger

    def getConsoleHandler(self):
        return self.consolehandler

    def getHandler(self):
        return self.handler


def mylogger():
    return MyLogger().getLogger()


def binary_search_for_error(insert_part, queries, conn):
    """Attempt to find errors in sql query using binary search method

    Parameters
    ----------
    insert_part : string
        ''INSERT INTO <table> (<columns>) VALUES''
    queries : list of strings
        ['(<values>)', '(<values>)', '(<values>)', '(<values>)', ...]
    server : string

    Returns
    -------
    insert_value : string
    insert_column : string
    """

    if not insert_part.endswith(' '):
        insert_part += ' '

    for i in range(len(queries)):
        if queries[i].endswith(','):
            queries[i] = queries[i][:-1]

    curs = conn.cursor()

    try:
        curs.execute(insert_part + ','.join(queries))
        conn.rollback()
        raise Exception('no error in query')
    except:
        pass

    length = None
    while len(queries) > 1:
        if len(queries) == length:
            raise Exception('exiting to escape infinite loop')

        length = len(queries)
        index = len(queries) / 2

        try:
            curs.execute(insert_part + ','.join(queries[:index]))
            conn.rollback()
        except:
            queries = queries[:index]
            continue

        try:
            curs.execute(insert_part + ','.join(queries[index:]))
            conn.rollback()
        except:
            queries = queries[index:]
            continue

    insert_columns = re.findall(r'.+ \((.+)\).+', insert_part)[0]
    insert_values = re.findall(r'\((.+)\)', queries[0])[0].split(',')
    insert_string = insert_part.replace(insert_columns, '{}')
    insert_columns = insert_columns.split(',')

    length = None
    while len(insert_values) > 1:
        if len(insert_values) == length:
            raise Exception('exiting to escape infinite loop')

        length = len(insert_values)
        index = len(insert_values) / 2

        try:
            sql = insert_string.format(','.join(insert_columns[:index])) + '(%s)' % ','.join(insert_values[:index])
            curs.execute(sql)
            conn.rollback()
        except:
            insert_columns = insert_columns[:index]
            insert_values = insert_values[:index]
            continue

        try:
            sql = insert_string.format(','.join(insert_columns[index:])) + '(%s)' % ','.join(insert_values[index:])
            curs.execute(sql)
            conn.rollback()
        except:
            insert_columns = insert_columns[index:]
            insert_values = insert_values[index:]
            continue
    try:
        curs.execute(sql)
        conn.rollback()
    except:
        print('Error found:\n{}'.format(sql))
    return insert_columns[0], insert_values[0]


def create_schema(df, flavor='postgres', output='strings'):
    """
    Parameters
    ----------
    df : pandas dataframe
    flavor : the output schema data types
    """
    schema_heirarchy = ('string', 'text', 'float', 'bigint', 'int', 'date', 'datetime')
    flavor_dict = {
        'postgres': ('varchar', 'text', 'double precision', 'bigint', 'int', 'date', 'timestamp'),
        'microsoft_sql': ('nvarchar', 'text', 'float', 'int', 'int', 'date', 'datetime'),
        'elasticsearch': ('string', 'string', 'float', 'long', 'integer', 'date', 'date')
    }
    flavor_dict = {k: dict(zip(schema_heirarchy, v)) for k, v in flavor_dict.iteritems()}
    df = df.copy()
    df = df.fillna('')
    for col in df.columns:
        df[col] = df[col].astype(str)
    data_types = []
    for col in df.columns:
        sub = df[col][df[col] != '']
        if sub.empty:
            data_types.append([col, 'string'])
        sub = set([detect_data_type(x) for x in set(sub)])
        if len(sub) == 1:
            data_types.append([col, sub.pop()])
        else:
            vc_lst = list(sub)
            for typ in schema_heirarchy:
                if typ in vc_lst:
                    data_types.append([col, typ])
                    break
    for row in data_types:
        if row[1] == 'string':
            sub = df[[row[0]]][df[row[0]] != '']
            if len(sub) == 0:
                row.append(1)
                continue
            max_len = sub.apply(lambda x: len(x[row[0]]), axis=1).max()
            if max_len > 4000:
                row[1] = 'text'
                row.append(False)
            else:
                row.append(int(max_len * 1.5))
        else:
            row.append(False)
        if row[1] == 'int':
            sub = df[row[0]][df[row[0]] != '']
            try:
                sub = sub.astype(int)
            except OverflowError:
                row[1] = 'bigint'

    new = pd.DataFrame(data=data_types, columns=['col', 'type', 'constraint'])
    new['type'] = new.apply(lambda x: flavor_dict[flavor][x['type']], axis=1)
    if output == 'strings':
        create = []
        for i, r in new.iterrows():
            if r['constraint']:
                create.append('{col} {type}({constraint}) DEFAULT NULL'.format(**r))
            else:
                create.append('{col} {type} DEFAULT NULL'.format(**r))
        return create
    elif output == 'df':
        return new
