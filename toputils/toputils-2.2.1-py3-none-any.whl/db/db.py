# -*- coding: utf-8 -*-

"""
top-db.db
~~~~~

Implement database class which can be used as context manager to
manage MySQL database connections and retrying failed queries/
connection attempts.

:copyright: (c) 2017 Peter Schutt
"""

import configparser
import logging
from pathlib import Path

import backoff
import mysql.connector

LOGGER = logging.getLogger(__name__)


class ConnectError(Exception):
    """ Custom connect error stops recursive retries when connection
    raises same exceptions being retried for execute method.

    """

    pass


class DataBase:
    """ Connection and query retry logic wrapper for mysql.connector.

    All necessary connection parameters must be located in a config
    file located in ~/.db/db.cnf or in any location passed to the
    DataBase.__init__ constructor as the cnf_dir param.

    Example cnf file:

    [test_db]
    user = user-name
    password = password1
    database = my-database
    host = 0.0.0.0
    charset = utf8
    ssl_ca = /dir/to/ca.pem
    ssl_cert = /dir/to/client-cert.pem
    ssl_key = /dir/to/client-key.pem

    """

    CONN = None

    def __init__(self, db_name, cnf_dir=None):
        """ Create a DataBase object.

        :param db_name: the name of the database that is being connected
            to. This is the section header of the config file that will
            be queried to get connection args.
        :param cnf_dif: (optional) Location of config file. Default location
            is ~/.db/db.cnf

        """
        if cnf_dir is None:
            cnf_dir = str(Path.home()) + "/.toputils/db.local"
        LOGGER.debug(f"Looking for config in {cnf_dir}")
        config = configparser.ConfigParser()
        config.read(cnf_dir)
        self.conn_args = dict(config[db_name])

    def __enter__(self):
        LOGGER.debug("Entering DB context manager")
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        LOGGER.debug("Exiting DB context manager")
        if exception_type is None:
            LOGGER.debug("No exception passed to __exit__")
            try:
                self.CONN.commit()
                LOGGER.debug("Commit changes")
            except AttributeError:
                # if called before connect
                LOGGER.debug("No established connection")
                pass
            except mysql.connector.errors.InternalError as e:
                if e.msg == "Unread result found":
                    LOGGER.debug("Exiting with unread results")
        self.close()

    @backoff.on_exception(backoff.expo,
                          ConnectError,
                          max_tries=5)
    def connect(self):
        """ Connect to mysql database.

        Passes all args found in configuration file as keyword arguments.

        :raises db.ConnectError:
        """
        LOGGER.debug("Creating database connection!")
        try:
            self.CONN = mysql.connector.connect(**self.conn_args)
        except (mysql.connector.errors.InterfaceError,
                mysql.connector.errors.OperationalError,
                mysql.connector.errors.ProgrammingError) as e:
            LOGGER.exception(str(e))
            raise ConnectError

    def close(self):
        """ Closes connection to mysql database."""
        LOGGER.debug("Attempting to close connection")
        try:
            self.CONN.close()
        except AttributeError:
            # if close called before connect
            LOGGER.debug("No connection to close!")
        else:
            LOGGER.debug("Connection closed")

    def commit(self):
        if self.CONN is not None:
            self.CONN.commit()

    @backoff.on_exception(backoff.expo,
                          (mysql.connector.errors.InterfaceError,
                           mysql.connector.errors.OperationalError),
                          max_tries=5)
    def execute(self, sql, data=None, many=False, dict_cursor=False):
        """ Executes the passed in sql statement.

        :param sql: MySQL query string. Can be parameterised.
        :param data: (optional) Query parameter values. Has to suit the
            query type, e.g. if many is True, needs to be a list of
            parameter value lists.
        :param many: (optional) Calls executemany() if True and execute()
            if false. Default False.
        :param dict_cursor: (optional) If True, results will be dict
            resembling {field_name: field_value, ..}. If False, results
            are lists in same order of field values in query. Default
            False.
        :rtype: mysql.connector.cursor
        """
        LOGGER.debug(f"execute method called with many={many},"
                     f"dict_cursor={dict_cursor}")
        if self.CONN is None:
            LOGGER.debug("No established connection!")
            self.connect()
        try:
            cursor = self.CONN.cursor(dictionary=dict_cursor)
        except (mysql.connector.errors.OperationalError) as e:
            LOGGER.exception(str(e))
            if e.msg == "MySQL Connection not available.":
                LOGGER.debug("Connection not available :(")
                self.CONN = None
            raise

        args = [sql, data] if data else [sql]
        func = cursor.executemany if many else cursor.execute
        LOGGER.debug(f"Calling {func} with {args}")
        func(*args)
        return cursor
