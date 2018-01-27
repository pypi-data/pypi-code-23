# -*- coding: utf-8 -*-
import datetime as dt
import os
import random
import string
import sys
import time

import pandas as pd
import yaml
from past.builtins import basestring

this_dir = os.path.dirname(__file__)


def get_config(prog=None):
    cfg_file = os.path.join(this_dir, 'conf.yaml')

    with open(cfg_file, 'r') as f:
        config = yaml.load(f)

    if prog is None:
        return config

    try:
        return config[prog]
    except KeyError:
        print('No config found for {}. Exiting now.'.format(prog))
        sys.exit(1)


def connect_db(server):
    db_conn = get_config('db_creds')[server]
    flavor = db_conn.pop('flavor')
    if flavor == 'mysql':
        import MySQLdb as connector
    elif flavor == 'postgres':
        import psycopg2 as connector
    elif flavor == 'mssql':
        import pymssql as connector
    else:
        raise KeyError('%s not supported' % server)
    conn = connector.connect(**db_conn)
    curs = conn.cursor()
    return curs, conn


class DBRouter(object):
    def __init__(self, databases):
        if isinstance(databases, basestring):
            databases = [databases]
        self.databases = databases
        self.cursors = {}
        self.connections = {}
        for db in databases:
            self.cursors[db], self.connections[db] = connect_db(db)

    def close(self):
        for db in self.databases:
            self.cursors[db].close()
            try:
                self.connections[db].close()
            except:
                pass

    def __getitem__(self, key):
        return self.cursors[key], self.connections[key]


def create_test_dataframe():
    start = dt.datetime.now()
    end = start + dt.timedelta(days=600)
    start = time.mktime(start.timetuple())
    end = time.mktime(end.timetuple())

    data = []
    for _ in range(500):
        astring = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randint(1, 50)))
        aninteger = random.randint(-100, 100)
        afloat = random.uniform(random.randint(-50, 0), random.randint(0, 50))
        randtime = start + (end - start) * random.random()
        adate = dt.date.fromtimestamp(randtime)
        adatetime = dt.datetime.fromtimestamp(randtime)
        row = [astring, aninteger, afloat, adate, adatetime]
        data.append(row)
    return pd.DataFrame(data=data, columns=['astring', 'aninteger', 'afloat', 'adate', 'adatetime'])
