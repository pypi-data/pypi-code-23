from itertools import product, starmap
from typing import overload, List, Dict, Optional, Tuple, Iterable

import rethinkdb as R

from .query import QueryBiStatement, QueryAndStatement, EmptyQueryStatement, StatementType, Interval, QueryAst, QueryRow

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['RethinkDBQueryParser', 'QueryBuildException']


class QueryBuildException(Exception):

    """
    Exception on query building
    """


class RethinkDBQueryParser:

    @overload
    @classmethod
    def index_bounds(cls, statements: Iterable[QueryBiStatement]) -> Optional[Tuple[bool, bool]]:
        pass

    @overload
    @classmethod
    def index_bounds(cls, statements: Iterable[QueryBiStatement]) -> Optional[bool]:  # pylint: disable=function-redefined
        pass

    @classmethod
    def index_bounds(cls, statements: Iterable[QueryBiStatement]):  # pylint: disable=function-redefined,too-many-branches
        right_close = None
        left_close = None
        bound_statements = [
            StatementType.bound, StatementType.ge, StatementType.gt,
            StatementType.le, StatementType.lt
        ]
        for statement in filter(lambda x: x.statement_type in bound_statements, statements):
            if statement.statement_type == StatementType.le and right_close is None or right_close:
                right_close = True
            elif statement.statement_type == StatementType.lt and right_close is None or not right_close:
                right_close = False
            elif statement.statement_type == StatementType.ge and left_close is None or left_close:
                left_close = True
            elif statement.statement_type == StatementType.gt and left_close is None or not left_close:
                left_close = False
            elif statement.statement_type == StatementType.bound:
                if left_close is None or left_close == statement.right.left_close:
                    left_close = statement.right.left_close
                else:
                    return None
                if right_close is None or right_close == statement.right.right_close:
                    right_close = statement.right.right_close
                else:
                    return None
            else:
                return None
        if right_close is None and left_close is None:
            return False
        return left_close, right_close

    @classmethod
    def wrap_bound(cls, bound: bool) -> str:
        return 'closed' if bound else 'open'

    @classmethod
    def wrap_bounds(cls, index_bounds: Tuple[bool, bool], default_value: bool) -> Tuple[str, str]:
        return cls.wrap_bound(index_bounds[0] or default_value), cls.wrap_bound(index_bounds[1] or default_value)

    @classmethod
    def secondary_indexes_query(  # pylint: disable=too-many-branches,too-many-locals
            cls, search_query: R.RqlQuery, selected_index: str, simple_statements: Dict[str, QueryBiStatement]) -> R.RqlQuery:
        splited_index = selected_index.split(':')
        # According to https://github.com/python/mypy/issues/328
        index_bounds = cls.index_bounds((simple_statements[field] for field in splited_index))  # type: ignore
        isin_used = False
        if index_bounds is None:
            raise QueryBuildException("Cannot build query: inconsistency bounds for indexes")
        left_filter: List[List] = [[]]
        right_filter: List[List] = [[]]
        for statement_field in sorted(simple_statements.keys()):
            if statement_field in splited_index:
                statement: QueryBiStatement = simple_statements.get(statement_field)
                if statement.statement_type == StatementType.isin:
                    isin_used = True
                    if len(left_filter) == 1 and not left_filter[0]:
                        left_filter = [statement.right]
                        right_filter = [statement.right]
                    else:
                        left_filter = list(starmap(lambda base, new_value: base + [new_value], product(left_filter, statement.right)))
                        right_filter = list(starmap(lambda base, new_value: base + [new_value], product(right_filter, statement.right)))
                else:
                    new_left_filter = None
                    new_right_filter = None
                    if statement.statement_type in [StatementType.ge, StatementType.gt]:
                        new_left_filter = statement.right
                        new_right_filter = R.maxval
                    elif statement.statement_type in [StatementType.le, StatementType.lt]:
                        new_right_filter = statement.right
                        new_left_filter = R.minval
                    elif statement.statement_type == StatementType.eq:
                        new_right_filter = statement.right
                        new_left_filter = statement.right
                    elif statement.statement_type == StatementType.bound:
                        new_left_filter = statement.right.left_bound
                        new_right_filter = statement.right.right_bound
                    for filter_list in left_filter:
                        filter_list.append(new_left_filter)
                    for filter_list in right_filter:
                        filter_list.append(new_right_filter)
        if isinstance(index_bounds, bool):
            if len(left_filter) == 1 and len(splited_index) == 1:
                return search_query.get_all(*left_filter[0], index=selected_index)
            return search_query.get_all(*left_filter, index=selected_index)
        if len(left_filter) > 1:
            raise QueryBuildException("Cannot use multiply index with between statement, please rewrite query or write query via rethinkdb")
        if len(left_filter[0]) == 1:
            # Just base unpack, to fix privous initial pack
            left_filter = left_filter[0]
            right_filter = right_filter[0]
        # Fix bound to not have None value
        default_bound_value = False
        if isin_used:
            if index_bounds[0] is False or index_bounds[1] is False:
                raise QueryBuildException("Cannot build valid query with one_of and between, please rewrite query or write query via rethinkdb")
            default_bound_value = True
        left_bound, right_bound = cls.wrap_bounds(index_bounds, default_bound_value)
        return search_query.between(
            left_filter[0], right_filter[0], index=selected_index,
            left_bound=left_bound, right_bound=right_bound
        )

    @classmethod
    def process_simple_statement(cls, search_query: R.RqlQuery, statement: QueryBiStatement) -> R.RqlQuery:
        row = R.row[statement.left.row_name]
        if statement.statement_type == StatementType.isin:
            rethinkdb_expr = R.expr(statement.right)
            return search_query.filter(lambda doc: rethinkdb_expr.contains(doc[statement.left.row_name]))
        if statement.statement_type == StatementType.bound:
            interval: Interval = statement.right
            if interval.left_close and interval.right_close:
                return search_query.filter((row >= interval.left_bound) & (row <= interval.right_bound))
            if interval.left_close and not interval.right_close:
                return search_query.filter((row >= interval.left_bound) & (row < interval.right_bound))
            if not interval.left_close and interval.right_close:
                return search_query.filter((row > interval.left_bound) & (row <= interval.right_bound))
            if not interval.left_close and not interval.right_close:
                return search_query.filter((row > interval.left_bound) & (row < interval.right_bound))
        return search_query.filter(getattr(row, f'__{statement.statement_type.name}__')(statement.right))

    @classmethod
    def process_complicated_statement(cls, search_query: R.RqlQuery, statement: QueryBiStatement) -> R.RqlQuery:
        if not isinstance(statement, QueryBiStatement):
            raise QueryBuildException("Unsupported query ast type to build")
        if statement.statement_type == StatementType.isin:
            if isinstance(statement.left, QueryRow):
                return search_query.filter(lambda doc: doc[statement.right.row_name].contains(doc[statement.left.row_name]))
            return search_query.filter(lambda doc: doc[statement.right.row_name].contains(doc[statement.left]))
        if statement.statement_type == StatementType.bound:
            raise QueryBuildException("How did you even get here?")
        return search_query.filter(
            getattr(R.row[statement.left.row_name], f'__{statement.statement_type.name}__')(R.row[statement.right.row_name])
        )

    @classmethod
    def process_simple_not_indexes_statements(  # pylint: disable=invalid-name
            cls, search_query: R.RqlQuery, simple_fields: List[str],
            simple_statements: Dict[str, QueryBiStatement]) -> R.RqlQuery:
        for simple_field in simple_fields:
            statement = simple_statements.get(simple_field, None)
            if statement:
                search_query = cls.process_simple_statement(search_query, statement)
        return search_query

    @classmethod
    def process_complicated_not_indexes_statements(  # pylint: disable=invalid-name
            cls, search_query: R.RqlQuery, complicated_statements: List[QueryBiStatement]) -> R.RqlQuery:
        for statement in complicated_statements:
            search_query = cls.process_complicated_statement(search_query, statement)
        return search_query

    @classmethod
    def split_query(cls, query: QueryAst) -> Tuple[Dict[str, QueryBiStatement], List[QueryBiStatement]]:
        if not isinstance(query, QueryAndStatement):
            if not isinstance(query, QueryBiStatement):
                raise QueryBuildException("Unsupported query ast type here")
            if query.complicated:
                return {}, [query]
            return {query.left.row_name: query}, []
        simple_statements: Dict[str, QueryBiStatement] = {}
        complicated_statements: List[QueryBiStatement] = []
        for sub_query in query._args:
            if not isinstance(sub_query, QueryBiStatement):
                raise QueryBuildException("Unsupported query ast type here")
            if not sub_query.complicated:
                simple_statements[sub_query.left.row_name] = sub_query
            else:
                complicated_statements.append(sub_query)
        return simple_statements, complicated_statements

    @classmethod
    def build_query(cls, model_class, query: QueryAst) -> R.RqlQuery:
        """
        Process query building in three steps:
        1. Simple indexes part
        2. Simple not indexed part
        3. Complicated not indexed part
        """
        if isinstance(query, EmptyQueryStatement):
            return R.table(model_class._table).filter(lambda doc: False)
        search_query = R.table(model_class._table)
        simple_statements, complicated_statements = cls.split_query(query)
        secondary_indexes: List[str] = []
        simple_fields: List[str] = []
        for field_name in simple_statements:
            if field_name in model_class._fields and model_class._fields.get(field_name).secondary_index:
                secondary_indexes.append(field_name)
            else:
                simple_fields.append(field_name)
        if secondary_indexes:
            selected_index, unused_fields = model_class.get_index_policy().select_secondary_index(secondary_indexes)
            if unused_fields:
                simple_fields.extend(unused_fields)
            search_query = cls.secondary_indexes_query(search_query, selected_index, simple_statements)
        search_query = cls.process_simple_not_indexes_statements(search_query, simple_fields, simple_statements)
        search_query = cls.process_complicated_not_indexes_statements(search_query, complicated_statements)
        return search_query
