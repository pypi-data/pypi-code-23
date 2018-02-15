"""
Database connection and checks
"""

import psycopg2


class DatabaseStatus(object):
    """
    Main object to connect to database and check it's status
    """

    def __init__(self, configuration):
        self.configuration = configuration

    def __repr__(self):
        return self.configuration['connection']['dbname']

    @property
    def connection(self):
        """
        Connect to database
        """
        return psycopg2.connect(**self.configuration['connection'])

    @property
    def is_slave(self):
        """
        Check if server is slave
        """
        cursor = self.connection.cursor()
        cursor.execute("""SELECT pg_is_in_recovery()""")
        return cursor.fetchone()[0]

    @property
    def is_readonly(self):
        """
        Check if database is in read-only mode
        """
        cursor = self.connection.cursor()
        cursor.execute("""SHOW transaction_read_only""")
        return cursor.fetchone()[0] != 'off'
