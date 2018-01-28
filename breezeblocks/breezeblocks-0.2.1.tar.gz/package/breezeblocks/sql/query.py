from collections import namedtuple

from ..exceptions import QueryError

from .column import AliasedColumnExpr
from .column_collection import ColumnCollection
from .expressions import _ValueExpr
from .query_components import TableExpression
from .table import AliasedTableExpression

class Query(TableExpression):
    """Represents a database query.
    
    This can be executed to fetch rows from the corresponding database, or it
    can be used as a table expression for other queries.
    """
    
    def __init__(self, spec, statement, params, db=None):
        """Initializes a query against a specific database.
        
        :param db: The database to perform the query on.
        :param spec: The spec for the expressions used to build this query.
        :param statement: The generated SQL this query represents.
        :param params: The parameters to pass to the cursor along with the SQL.
        """
        if db is None:
            raise QueryError('Attempting to query without a database.')
        
        self._db = db
        
        self._spec = spec
        self._statement = statement
        self._params = params
        
        self._columns = _QueryColumnCollection(self)
        self._return_type = namedtuple('QueryResult_'+str(id(self)),
            self._columns.getNames(), rename=True)
    
    @property
    def columns(self):
        return self._columns
    
    def execute(self, limit=None, offset=None):
        """Fetch rows in this query from the database.
        
        :param limit: LIMIT argument for this execution.
        :param offset: OFFSET argument for this execution.
        
        :return: The rows returned by the query.
        """
        statement = self._statement
        if limit is not None:
            if offset is not None:
                statement += '\nLIMIT {0} OFFSET {0}'.format(limit, offset)
            else:
                statement += '\nLIMIT ' +str(limit)
        
        results = []
        
        with self._db.pool.get() as conn:
            cur = conn.cursor()
            cur.execute(statement, self._params)
            results = cur.fetchall()
            cur.close()
        
        return [ self._process_result(r) for r in results ]
    
    def show(self):
        """Show the constructed SQL statement for this query."""
        print(self._statement, self._params, sep='\n')
    
    def getColumn(self, key):
        return self._columns[key]
    
    def as_(self, alias):
        return AliasedQuery(self, alias)
    
    def _process_result(self, r):
        """Constructs an object of the correct return type from a result row."""
        return self._return_type._make(r)
    
    def _get_from_field(self):
        return '({})'.format(self._statement)
    
    def _get_selectables(self):
        return [ self._columns[name] for name in self._columns.getNames() ]
    
    def _get_params(self):
        return self._params
    
    def _get_statement(self):
        return self._statement

class AliasedQuery(AliasedTableExpression):
    """A finalized query that has been given an alias.
    
    This class is only for use as a table expression in other queries.
    """
    
    def __init__(self, query, alias):
        super().__init__(query, alias)
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, other):
        if isinstance(other, AliasedQuery):
            return self._alias == other._alias and self._table_expr == other._table_expr
        else:
            return False

class _QueryColumn(_ValueExpr):
    """Represents a column from a non-aliased query.
    
    Columns from non-aliased queries behave subtly differently than most
    columns, and those small differences are handled by this class.
    """
    
    def __init__(self, column, query):
        self._query = query
        self._column = column
    
    def _get_name(self):
        return self._column._get_name()
    
    def _get_ref_field(self):
        return self._get_name()
    
    def _get_select_field(self):
        return self._get_name()
    
    def _get_tables(self):
        return {self._query}
    
    def as_(self, alias):
        return AliasedColumnExpr(self, alias)

class _QueryColumnCollection(ColumnCollection):
    def __init__(self, query):
        self._query = query
        columns = [_QueryColumn(expr, query) for expr in query._spec.select_exprs]
        super().__init__(columns)
    
    def _get_tables(self):
        return {self._query}
