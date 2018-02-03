from .exceptions import MissingModuleError
from .pool import ConnectionPool as Pool
from .query_builder import QueryBuilder
from .dml_builders import InsertBuilder, UpdateBuilder, DeleteBuilder

class Database(object):
    """Proxies the database at the URI provided."""
    
    def __init__(self, connect_args=None, connect_kwargs=None,
            dbapi_module=None, dsn=None, minconn=10, maxconn=20):
        """Refer to your DBAPI module documentation for what the content
        of `connect_args` and `connect_kwargs` should be.
        
        :param connect_args: *args for calls to `dbapi.connect`.
        :param connect_kwargs: **kwargs for calls to `dbapi.connect`.
        :param dbapi_module: The DBAPI 2.0 module to use for this database.
        :param dsn: The DSN (connection string) for this database.
          This will be pre-pended to `connect_args` if present.
        :param minconn: Number of standby connections for this database.
        :param maxconn: Limit on open connections to this database.
        """
        self._dsn = dsn
        self._dbapi = dbapi_module
        
        if self._dbapi is None:
            raise MissingModuleError()
        
        connect_args = connect_args if connect_args is not None else []
        connect_kwargs = connect_kwargs if connect_kwargs is not None else {}
        
        if dsn is not None:
            connect_args.insert(0, dsn)
        
        self.pool = Pool(self._dbapi, minconn, maxconn,
            *connect_args, **connect_kwargs)
    
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
