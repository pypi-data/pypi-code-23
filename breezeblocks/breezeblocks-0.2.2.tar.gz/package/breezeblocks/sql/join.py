from .query_components import TableExpression
from .expressions import _ValueExpr
from .column_collection import ColumnCollection
from ..exceptions import QueryError

class _JoinColumn(_ValueExpr):
    """A column used through a join expression."""
    
    def __init__(self, join_expr, column_expr):
        self._join_expr = join_expr
        self._column_expr = column_expr
    
    def _get_name(self):
        return self._column_expr._get_name()
    
    def _get_ref_field(self):
        return self._column_expr._get_ref_field()
    
    def _get_select_field(self):
        return self._column_expr._get_select_field()
    
    def _get_tables(self):
        return set((self._join_expr,))

class _JoinedTable(ColumnCollection):
    """A table that is one side of a join expression."""
    
    def __init__(self, join_expr, table):
        self._join_expr = join_expr
        self._table = table
        
        join_columns = [_JoinColumn(join_expr, column) for column in table._get_selectables()]
        super().__init__(join_columns)
    
    def _get_tables(self):
        return {self._join_expr}
    
    def _get_from_field(self):
        return self._table._get_from_field()

class _Join(TableExpression):
    """Represents a join of two table expressions."""
    
    def __init__(self, left, right):
        """Creates a join for the left and right expressions."""
        self._left = _JoinedTable(self, left)
        self._right = _JoinedTable(self, right)
    
    @property
    def left(self):
        return self._left
    
    @property
    def right(self):
        return self._right
    
    def getColumn(self, key):
        if not isinstance(key, str):
            raise TypeError('Tables require strings for lookup keys.')
        
        if key in self._left._columns:
            return self._left[key]
        elif key in self._right._columns:
            return self._right[key]
        else:
            raise KeyError()
    
    def __hash__(self):
        return hash((self._left._table, self._right._table))
    
    def __eq__(self, other):
        if (isinstance(other, self.__class__)):
            return (
                self._left._table == other._left._table and
                self._right._table == other._right._table
            )
        else:
            return False
    
    def _get_selectables(self):
        selectables = []
        selectables.extend(self._left._get_selectables())
        selectables.extend(self._right._get_selectables())
        return selectables
    
    def _get_params(self):
        params = []
        params.extend(self._left._table._get_params())
        params.extend(self._right._table._get_params())
        return params
    
    def _get_join_expression(self):
        raise NotImplementedError()

class _QualifiedJoin(_Join):
    """Represents a join with a 'USING' or 'ON' condition."""
    
    def __init__(self, left, right, *, on=None, using=None):
        super().__init__(left, right)
        
        if on is None and using is None:
            raise QueryError(
            'Qualified Join statements must have an ON or a USING condition.')
        
        if on is not None and using is not None:
            raise QueryError(
                'Join statement cannot have both ON and USING conditions.')
        
        self._on_exprs = on
        self._using_fields = using
    
    def _get_from_field(self):
        return self._get_join_expression() + ' ' + self._get_join_condition()
    
    def _get_join_condition(self):
        if self._on_exprs is not None:
            return 'ON {}'.format(
                ', '.join(expr._get_ref_field() for expr in self._on_exprs))
        elif self._using_fields is not None:
            return 'USING ({})'.format(', '.join(self._using_fields))
        else:
            raise QueryError(
                'A join condition must be specified for qualified joins.')

class CrossJoin(_Join):
    """Represents a cross join of two table expressions."""
    
    def _get_from_field(self):
        return self._get_join_expression()
    
    def _get_join_expression(self):
        return '{} CROSS JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())

class InnerJoin(_QualifiedJoin):
    """Represents an inner join of two table expressions."""
    
    def _get_join_expression(self):
        return '{} INNER JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())

class LeftJoin(_QualifiedJoin):
    """Represents a left outer join of two table expressions."""
    
    def _get_join_expression(self):
        return '{} LEFT JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())

class RightJoin(_QualifiedJoin):
    """Represents a right outer join of two table expressions."""
    
    def _get_join_expression(self):
        return '{} RIGHT JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())

class OuterJoin(_QualifiedJoin):
    """Represents a full outer join of two table expressions."""
    
    def _get_join_expression(self):
        return '{} OUTER JOIN {}'.format(
            self._left._get_from_field(), self._right._get_from_field())
