#!/usr/bin/env python
import sys
import MySQLdb
import vmtools
import collections

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
#from local_settings import *

class QuickMysql():
    """A class simplify common mysql tasks

    instance variables:
    self.placeholder
    """

    def __init__(self, dbhost, dbuser, dbpass, dbname=None):
        """set instance variables, set instance aws connections

        keyword arguments:
        :type exchange_plugin: string
        :param exchange_plugin: the name of the exchange plugin (exchange plugins available are those present in the exhchange_plugins directory, they must follow the format of the file poloniex.py (must have a class called 'ExchangeConnector' and have all the the same methods which must output the same format)
        :type api_key: string
        :param api_key: the api key for your exchange (see individual exchange plugins for more info)
        :type api_sec: string
        :param api_sec: the api sec key for your exchange (see individual exchange plugins for more info)
        """
        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbname = dbname


    def connect_to_database(self, dbhost=None, dbuser=None, dbpass=None, dbname=None):
        """Creates a connection to the database, returns the cursor object
        """
        dbhost = dbhost if dbhost is not None else self.dbhost
        dbuser = dbuser if dbuser is not None else self.dbuser
        dbpass = dbpass if dbpass is not None else self.dbpass
        dbname = dbname if dbname is not None else self.dbname
        con = MySQLdb.connect(dbhost, dbuser, dbpass, dbname)
        cur = con.cursor()
        return(cur, con)

    def connect_to_mysql(self, dbhost=None, dbuser=None, dbpass=None):
        """Creates a connection to the database, returns the cursor object
        """
        dbhost = dbhost if dbhost is not None else self.dbhost
        dbuser = dbuser if dbuser is not None else self.dbuser
        dbpass = dbpass if dbpass is not None else self.dbpass
        con = MySQLdb.connect(dbhost, dbuser, dbpass)
        cur = con.cursor()
        return(cur, con)

    def does_user_exist(self, dbuser, dbhost):
        # connect to mysql
        cur, con = self.connect_to_mysql()
        check_user_sql_cmd = "select  User, Host from  mysql.user where User='{}' and Host='{}'".format(dbuser, dbhost)
        check_user_sql_cmd_output = cur.execute(check_user_sql_cmd)
        if check_user_sql_cmd_output:
            return True
        else:
            return False

    def does_db_exist(self, dbname):
        # connect to mysql
        cur, con = self.connect_to_mysql()
        check_db_sql_cmd = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{}'".format(dbname)
        check_db_sql_cmd_output = cur.execute(check_db_sql_cmd)
        if check_db_sql_cmd_output:
            return True
        else:
            return False

    def column_as_list(self, table_name, column_name):
        # connect to mysql
        cur, con = self.connect_to_mysql()
        sql_cmd = 'select {} from {}'.format(column_name, table_name)
        cur.execute(sql_cmd)
        output = cur.fetchall()
        column_list = [ innertuple[0] for innertuple in output ]
        return column_list


    def close_database_connection(self, connection_object):
        connection_object.commit()
        connection_object.close()

    def create_database_user(self, dbuser, dbname, dbpass, host='localhost', privileges_list=[]):
        # connect to mysql
        cur, con = self.connect_to_mysql()
        # create user
        check_existence_user_cmd = "SELECT * FROM mysql.user WHERE user = '{}'".format(dbuser)
        check_existence_user_result = cur.execute(check_existence_user_cmd)
        if privileges_list:
            privileges_str = ' '.join(privileges_list)
        else:
            privileges_str = 'all privileges'
        if check_existence_user_result == 0:
            mysql_create_user_cmd = "grant {} on {}.* to '{}'@'{}' identified by '{}'".format( privileges_str, dbname, dbuser, host, dbpass)
            cur.execute(mysql_create_user_cmd)
        # close connection
        self.close_database_connection(connection_object=con)

    def create_database(self, dbname):
        """Creates the database required for all cryptocurrency_tools operations
        """
        # connect to mysql
        cur, con = self.connect_to_mysql()
        # create db
        check_existence_database_cmd = "SHOW DATABASES LIKE '{}'".format(dbname)
        check_existence_database_result = cur.execute(check_existence_database_cmd)
        if check_existence_database_result == 0:
            mysql_create_db_cmd = 'create database if not exists {}'.format(dbname)
            cur.execute(mysql_create_db_cmd)
        # close connection
        self.close_database_connection(connection_object=con)

    def execute_simple(self, sql_cmd):
        """Take market and rate and insert into the database
        keyword arguments:
        :type sql_cmd: str
        :param sql_cmd: the sql to execute
        """
        # connect to database
        cur, con = self.connect_to_database()
        cur.execute(sql_cmd)
        # close connection
        self.close_database_connection(connection_object=con)

    def execute_simple_output(self, sql_cmd):
        """Take sql_cmd, execute and return the output
        keyword arguments:
        :type sql_cmd: str
        :param sql_cmd: the sql to execute
        """
        # connect to database
        cur, con = self.connect_to_database()
        cur.execute(sql_cmd)
        output = cur.fetchall()
        # close connection
        self.close_database_connection(connection_object=con)
        return output

    def insert_many(self, sql_cmd, input_array, input_type, number_of_inserts_values=1 ):
        # TODO this probably won't work, and doesn't save much time
        """Loop through array and insert values
        keyword arguments:
        :type sql_cmd: str
        :param sql_cmd: the sql to execute
        :type input_array: dict, list or tuple
        :param input_array: the array with the key, value (dict) or list/tuple of values to insert
        :type input_type: str
        :param input_type: dict or sequence (list of lists or tuple of tuples)
        :type number_of_inserts_values: int
        :param number_of_inserts_values: the number of values to insert each time through the loop for dict this should be 1, for a sequence it is the length of inner-most sequence (ex: [[1,2,3], [4,5,6]] would be 3)
        """
        # connect to database
        cur, con = self.connect_to_database()
        cur.executemany("insert into balances values (%s , %s)", balances_dict.items())
        # close connection
        self.close_database_connection(connection_object=con)

    def create_table(self, table_name, column_dict):
        """Takes a table_name and column_dict, creates a table
        :type table_name: str
        :param table_name: the name for the table
        :type column_dict: dict
        :param column_dict: a ordered dictionary, created by using collections.OrderedDict() and passing it a list of two item tuples (first item is key, second is value), ex collections.OrderedDict([('order_id', 'bigint(50)'), ('trade_id', 'bigint(50)')]); this is essential to ensure the order of the columns
        """
        # connect to database
        cur, con = self.connect_to_database()
        check_existence_table_cmd = "SHOW TABLES LIKE '{}'".format(table_name)
        check_existence_result = cur.execute(check_existence_table_cmd)
        if check_existence_result == 0:
            columns_definitions = ', '.join("{!s} {!s}".format(key,val) for (key,val) in column_dict.items())
            mysql_create_table_cmd = "create table if not exists {} ( {} )".format(table_name, columns_definitions)
            cur.execute(mysql_create_table_cmd)
        # close connection
        self.close_database_connection(connection_object=con)
