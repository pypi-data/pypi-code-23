"""
A wrapper around SQLAlchemy functionality.
"""

import gc
import json
import os
import random

import pandas as pd
import sqlalchemy
from autoalchemy.dataframe_parser import DataframeParser
from autoalchemy.schema_code_generator import generate_sqlalchemy_schema_code
from autoalchemy.utils import (get_filename, listdir_full, make_valid_name,
                               parse_config, print_highlighted, time_function)


class ViewTableException(Exception):
    """A class to represent issues with querying Views and Tables."""
    pass


class AutoAlchemyWrapper:
    """A wrapper around SQLAlchemy to simplify database interactions.

    Connect to the database by providing the path to config.json or by passing
    the authentication details as parameters.

    Attributes:
        config_path (str): Path to the configuration file.
        host (str): Hostname of the server.
        user (str): Username of the MySQL user.
        password (str): Password for the user.
        port (int): Port number.
        verbose (int): Set to 0 to suppress verbose execution.
    """

    def __init__(self, config_path=None, host=None, user=None, password=None, db=None, port=3306, verbose=1):
        if config_path:
            self.auth = parse_config(config_path=config_path)
        else:
            self.auth = {'host': host, 'user': user, 'password': password, 'db': db, 'port': port}

        self._connection_string = self.create_mysql_connection_string(**self.auth)
        self.engine = sqlalchemy.create_engine(self._connection_string)
        self.conn = self.engine.connect()
        self.verbose = verbose

    @staticmethod
    def create_mysql_connection_string(host, user, password, db, port=3306):
        """Return a string with the SQLAlchemy formatted connection info."""
        conn_str = "mysql://{user}:{password}@{host}/{db}".format(
            host=host,
            user=user,
            password=password,
            db=db
        )
        return conn_str

    def _safe_execute(self, query):
        """Execute a query, fetch all results, and close the ResultProxy. Return None if query has no return value.

        Also handles various exceptions that may occur.
        """
        if not isinstance(query, str):
            raise ValueError('The query should be a single string with a SQL statement')

        # Execute query.
        try:
            result_proxy = self.conn.execute(query)
        except sqlalchemy.exc.ProgrammingError as e:
            if 'CREATE VIEW' in query.upper():
                raise ViewTableException('Invalid View creation.')
        except sqlalchemy.exc.OperationalError as e:
            if 'Unknown table' in str(e) and 'DROP TABLE' in query.upper():
                raise ViewTableException('Trying to drop a view with DROP TABLE')
            elif 'is not VIEW' in str(e) and 'DROP VIEW' in query.upper():
                raise ViewTableException('Trying to drop a table with DROP VIEW')
        except Exception as e:
            raise e

        # Parse response.
        response = None
        try:
            response = result_proxy.fetchall()
        except sqlalchemy.exc.ResourceClosedError as e:
            # If the error message has this substring, it's fine, and we can continue.
            if 'does not return rows' in str(e):
                return
            else:
                raise e

        result_proxy.close()
        return response

    def _getattr(self, attr):
        output = self._safe_execute('SHOW {attr}'.format(attr=attr))
        return [x.values()[0] for x in output]

    def tables(self):
        """A list of the tables."""
        return self._getattr('TABLES')

    def databases(self):
        """A list of the databases."""
        return self._getattr('DATABASES')

    def _drop(self, keyword):
        assert keyword in  ['TABLE', 'VIEW']

        tables = self.tables()
        n = 0

        for table in tables:
            query = 'DROP {keyword} {table};'.format(keyword=keyword, table=table)
            try:
                self._safe_execute(query=query)
                n += 1
            except ViewTableException:
                continue

        self._verbose_print('Nuked all {0} {1}s in database: {2}'.format(n, keyword.lower(), self.auth['db']))

    def drop_all_tables(self):
        self._drop(keyword='TABLE')

    def drop_all_views(self):
        self._drop(keyword='VIEW')

    def _create_test_tables(self, n=5):
        """Create n random tables, for testing only."""
        self._verbose_print('Creating {} random test tables...'.format(n))
        for _ in range(n):
            random_num = random.randint(0, 2000)
            cmd = "CREATE TABLE test_table_{i} (column_1 VARCHAR(20), column_2 VARCHAR(20))"
            cmd = cmd.format(i=random_num)
            self._safe_execute(cmd)
            self._verbose_print(cmd)

    def create_new_schema(self, declarative_base):
        """Push a new schema to the connection."""
        declarative_base.metadata.create_all(self.engine)
        self._verbose_print('Pushed schema to: {0}.'.format(self._connection_string))

    def create_view(self, raw_query, view_name=None):
        """Create a new view in the database.

        Args:
            raw_query (str): A valid SQL statement, or the path to a .sql file.
            view_name (str): The name of the view. Will be parsed from the name of the file, if not provided.
        """
        if raw_query.endswith('.sql'):
            if not os.path.exists(raw_query):
                raise ValueError("The path {0} doesn't exist".format(raw_query))
            with open(raw_query, 'r') as fp:
                query = '\n'.join(fp.readlines())
            fname = os.path.basename(raw_query)
            view_name = view_name or fname.replace('.sql', '')
        else:
            query = raw_query
            if not view_name:
                raise ValueError('Must provide a view name, if using a raw query.')

        view_query = 'CREATE VIEW {view_name} AS {query}'.format(view_name=view_name, query=query)
        self._safe_execute(view_query)

    def create_views_in_directory(self, dir_path):
        """Read all .sql files from a directory and execute them."""
        files = listdir_full(dir_path)
        for file_path in files:
            if file_path.endswith('.sql'):
                self._verbose_print('Creating view from: {0}'.format(file_path))
                self.create_view(file_path)

    def create_table(self, dfparser, head=True, garbage_collect=True):
        """Fill a table described by a DataframeParser object. Uses pd.DataFrame.to_sql().

        Args:
            dfparser (DataframeParser)
            head (bool): If True, push only the heads of the dataframes, for testing.
            garbage_collect (bool): If True, after pushing to the database, dereference the dataframe and
                call the garbage collector. Might be helpful when working with large
                datasets on low-memory hardware.
        """
        if head:
            df = dfparser.head
        else:
            df = dfparser.dataframe

        df.columns = [make_valid_name(col) for col in df.columns]
        df.to_sql(name=dfparser.name, con=self.engine, if_exists='replace', index=False)

        if garbage_collect:
            del df
            gc.collect()

    def create_all_tables(self, df_parser_list, head=True):
        """Push all wrapped dataframes to the SQL server.

        Args:
            df_parser_list (List[DataframeParser])
            head (bool): If True, push only the heads of the dataframes, for testing.
        """
        for i, dfparser in enumerate(df_parser_list):

            if self.verbose > 0:
                _, filename = os.path.split(dfparser.file_path)
                filename = filename.rjust(50, ' ')
                msg = 'Pushing ({i}/{n}): {filename}  ==>  {table}'
                msg = msg.format(i=str(i).rjust(2, '0'), n=len(df_parser_list), filename=filename, table=dfparser.name)
                self._verbose_print(msg)

            self.create_table(dfparser, head=head)

    def _verbose_print(self, msg):
        if self.verbose > 0:
            print(msg)
