from .exceptions import MissingModuleError
from .pool import ConnectionPool as Pool
from .query_builder import QueryBuilder
from .dml_builders import InsertBuilder, UpdateBuilder, DeleteBuilder

class Database(object):
    """Proxies the database at the URI provided."""
    def __init__(self, dsn, dbapi_module=None, *args,
            minconn=10, maxconn=20, **kwargs):
        self._dsn = dsn
        self._dbapi = dbapi_module
        
        if self._dbapi is None:
            raise MissingModuleError()
        
        self._connection_args = args
        self._connection_kwargs = kwargs
        
        self.pool = Pool(self._dbapi, minconn, maxconn,
            dsn, *args, **kwargs)
    
    def query(self, *queryables):
        """Starts building a query in this database.
        
        Any arguments should be selectable expressions, such as columns or
        values that should end up in the result rows of the query.
        """
        return QueryBuilder(self).select(*queryables)
    
    def insert(self, table, columns=[]):
        """Starts building an insert in this database.
        
        :param table: The table to insert into.
        :param columns: A list of the columns to set values of.
        :return: An Insert builder for the table and columns provided.
        """
        return InsertBuilder(table, columns, db=self)
    
    def update(self, table):
        """Starts building an update in this database.
        
        :param table: The table to update rows of.
        :return: An Update builder for the table provided.
        """
        return UpdateBuilder(table, db=self)
    
    def delete(self, table):
        """Starts building a delete in this database.
        
        :param table: The table to delete rows from.
        :return: A delete builder for the table provided.
        """
        return DeleteBuilder(table, db=self)
    
    def connect(self):
        """Returns a new connection to the database."""
        return self._dbapi.connect(self._dsn,
            *self._connection_args, **self._connection_kwargs)
