#!/usr/bin/env python
# coding: utf-8

from dotenv import load_dotenv
from os import environ
import psycopg2


def make_psql_args(envfile):
    load_dotenv(envfile)

    opts = {}
    opts['dbname'] = environ.get("PGDBNAME")
    opts['user'] = environ.get("PGUSER")
    if environ.get("PGPASSWORD"):
        opts['password'] = environ.get("PGPASSWORD")
    if environ.get("PGHOST"):
        opts['host'] = environ.get("PGHOST")
    if environ.get("PGPORT"):
        opts['port'] = environ.get("PGPORT")

    return opts


class pgsql:
    def __init__(self, schema='public', envfile='.env'):
        self.conn = None
        self.cur = None
        self.schema = schema
        self.envfile = envfile

        self.args = make_psql_args(self.envfile)
        self.dbname = self.args['dbname']

    def __enter__(self):
        dsn = ' '.join('{}={}'.format(key, value) for key, value in self.args.items())
        self.conn = psycopg2.connect(dsn)
        self.cur = self.conn.cursor()

        return self

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def fqn(self, table):
        return '%s.%s.%s' % (self.dbname, self.schema, table)
