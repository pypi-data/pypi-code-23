# -*- coding: utf-8 -*-
import os
import logging
from sqlwriter.configuration import SUPPORTED_DATABASES, get_config
from sqlwriter.exceptions import SQLWriterConfigException,SQLWriterImportException

logger = logging.getLogger(__name__)

def connect_db(flavor):
    package_dir = os.path.abspath(os.path.join(__file__, '../../..'))
    config_file = os.path.join(package_dir, 'tests', 'test_conf.yaml')

    try:
        creds = get_config(config_file, 'db_creds')[flavor]
    except KeyError:
        raise SQLWriterConfigException('%s not in db_creds config' % flavor)

    if flavor == 'mysql':
        try:
            import MySQLdb as connector
        except ImportError:
            raise SQLWriterImportException('No module named MySQLdb')

    elif flavor == 'postgres':
        import psycopg2 as connector
    else:
        raise SQLWriterConfigException('%s no supported' % flavor)

    conn = connector.connect(**creds)
    curs = conn.cursor()
    return conn, curs


def initdb(arg):
    for db in SUPPORTED_DATABASES:
        try:
            curs, conn = connect_db(db)
        except Exception as e:
            logger.error(e)
