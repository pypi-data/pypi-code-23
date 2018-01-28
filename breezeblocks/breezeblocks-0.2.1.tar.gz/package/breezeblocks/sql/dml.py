from ..exceptions import InsertError, UpdateError, DeleteError
from .query import Query

class Insert(object):
    """Represents a database insert.
    
    This can be used to insert data either from your python processes or from
    the database itself using insert-into-select.
    """
    
    def __init__(self, statement_base, table, columns, db=None):
        """Initializes an insert statement against a specific database.
        
        :param statement_base: The first part of the insert statement.
        :param table: The table to insert into.
        :param columns: The columns that data is being inserted in.
        :param db: The database to perform the insert on.
        """
        if db is None:
            raise InsertError('Attempting to insert without a database.')
        
        self._db = db
        self._statement_base = statement_base
        self._table = table
        self._columns = columns
        
    def execute(self, data):
        """Insert rows from data into the database.
        
        The "data" provided can either be a query or actual data.
        
        For a query, this will execute an insert-into-select statement
        in the database.
        
        For in-memory data in python, this translated to a `cursor.executemany`
        call. The data should be a list of suitable objects, which at this time
        is limited to lists or tuples.
        
        :param data: The query or rows to insert.
        """
        if isinstance(data, Query):
            self._insert_from_query(data)
        else:
            self._insert_row_data(data)
    
    def show(self):
        """Show the constructed SQL for this insert statement."""
        if self._db._dbapi.paramstyle == 'qmark':
            param_marker = '?'
        elif self._db._dbapi.paramstyle in ['format', 'pyformat']:
            param_marker = '%s'
        else:
            param_marker = '?'
        
        print(self._statement_base + ' VALUES ({0})'.format(','.join(param_marker for _ in self._columns)))
    
    def _insert_from_query(self, query):
        statement = self._statement_base + '\n' + query._get_statement()
        params = query._get_params()
        
        with self._db.pool.get() as conn:
            cur = conn.cursor()
            cur.execute(statement, params)
            cur.close()
            conn.commit()
    
    def _insert_row_data(self, data):
        if self._db._dbapi.paramstyle == 'qmark':
            param_marker = '?'
        elif self._db._dbapi.paramstyle in ['format', 'pyformat']:
            param_marker = '%s'
        else:
            raise InsertError('DBAPI module has unsupported parameter style.')
        
        statement = self._statement_base + ' VALUES ({0})'.format(','.join(param_marker for _ in self._columns))
        
        with self._db.pool.get() as conn:
            cur = conn.cursor()
            cur.executemany(statement, data)
            cur.close()
            conn.commit()

class Update(object):
    """Represents a database update."""
    
    def __init__(self, statement, params, db=None):
        """Initializes an update statement against a specific database.
        
        :param statement: The SQL statement for the update.
        :param params: A list of literal values to pass into the statement.
        :param db: The database to perform the update on.
        """
        if db is None:
            raise UpdateError('Attempting to update without a database.')
        
        self._db = db
        self._statement = statement
        self._params = params
    
    def execute(self):
        """Executes the update in the database."""
        with self._db.pool.get() as conn:
            cur = conn.cursor()
            cur.execute(self._statement, self._params)
            cur.close()
            conn.commit()
    
    def show(self):
        """Show the constructed SQL statement for this update."""
        print(self._statement, self._params, sep='\n')

class Delete(object):
    """Represents a database delete."""
    
    def __init__(self, statement, params, db=None):
        """Initializes a delete statement against a specific database.
        
        :param statement: The SQL statement for the delete.
        :param params: A list of literal values to pass into the statement.
        :param db: The database to perform the delete on.
        """
        if db is None:
            raise DeleteError('Attempting to delete without a database.')
        
        self._db = db
        self._statement = statement
        self._params = params
    
    def execute(self):
        """Executes the delete in the database."""
        with self._db.pool.get() as conn:
            cur = conn.cursor()
            cur.execute(self._statement, self._params)
            cur.close()
            conn.commit()
    
    def show(self):
        """Show the constructed SQL statement for this delete."""
        print(self._statement, self._params, sep='\n')
