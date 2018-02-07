from abc import ABC, abstractmethod
from enum import Enum
import logging
from typing import Set

from lazy import lazy

from ..utils import prettify_value

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'QueryRow', 'QueryBiStatement', 'StatementType', 'QueryAndStatement', 'Interval',
    'EmptyQueryStatement', 'QueryAst'
]

_log = logging.getLogger(__name__)


class Interval:

    __slots__ = ['left_bound', 'right_bound', 'left_close', 'right_close']

    def __init__(
            self, left_bound, right_bound,
            left_close: bool = False, right_close: bool = False) -> None:
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.left_close = left_close
        self.right_close = right_close

    def contains_interval(self, other: 'Interval') -> bool:
        if self.left_bound > other.left_bound:
            return False
        if self.left_bound == other.left_bound and other.left_close and not self.left_close:
            return False
        if self.right_bound < other.right_bound:
            return False
        if self.right_bound == other.right_bound and other.right_close and not self.right_close:
            return False
        return True

    def clone(self) -> 'Interval':
        return Interval(
            self.left_bound,
            self.right_bound,
            left_close=self.left_close,
            right_close=self.right_close
        )

    @property
    def valid(self):
        if self.left_bound < self.right_bound:
            return True
        return self.left_bound == self.right_bound and self.left_close and self.right_close

    def __eq__(self, other) -> bool:
        if not isinstance(other, Interval):
            return False
        return self.left_bound == other.left_bound and self.right_bound == other.right_bound and self.left_close == other.left_close and self.right_close == other.right_close

    def __contains__(self, item) -> bool:
        return (
            ((self.left_bound < item) or (self.left_close and self.left_bound == item)) and
            ((self.right_bound > item) or (self.right_close and self.right_bound == item))
        )

    def __str__(self) -> str:
        return f"{'[' if self.left_close else '('}{self.left_bound}, {self.right_bound}{']' if self.right_close else ')'}"


class QueryBuildException(Exception):

    pass


class StatementType(Enum):

    eq = '=='  # pylint: disable=invalid-name
    lt = '<'  # pylint: disable=invalid-name
    gt = '>'  # pylint: disable=invalid-name
    ne = '!='  # pylint: disable=invalid-name
    le = '<='  # pylint: disable=invalid-name
    ge = '>='  # pylint: disable=invalid-name
    isin = 'in'  # pylint: disable=invalid-name
    bound = 'bound'  # pylint: disable=invalid-name


class QueryAst:

    __slots__ = ['_args']
    _args_order_important = True

    def __init__(self, *args) -> None:
        self._args = list(args)

    def _is_same_ordered_args_check(self, other: 'QueryAst') -> bool:
        for index, arg in enumerate(self._args):
            opposite_arg = other._args[index]  # type: ignore
            if opposite_arg.__class__ != arg.__class__:
                return False
            if not isinstance(arg, QueryAst) and arg != opposite_arg:
                return False
            if isinstance(opposite_arg, QueryAst) and not arg.is_same(opposite_arg):
                return False
        return True

    def _is_same_unordered_args_check(self, other: 'QueryAst') -> bool:
        for arg in self._args:
            opposite_arg = None
            if hasattr(arg, 'is_same'):
                opposite_arg = next(filter(arg.is_same, other._args), None)  # pylint: disable=cell-var-from-loop
            else:
                opposite_arg = next(filter(lambda x: arg == x, other._args), None)  # pylint: disable=cell-var-from-loop
            if opposite_arg is None:
                return False
        return True

    def is_same(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if len(self._args) != len(other._args):  # type: ignore
            return False
        if self._args_order_important:
            if not self._is_same_ordered_args_check(other):  # type: ignore
                return False
        else:
            if not self._is_same_unordered_args_check(other):  # type: ignore
                return False
        return True

    def merge(self, _other: 'QueryAst') -> 'QueryAst':
        raise QueryBuildException(f"{self.__class__.__name__} cannot be merged with anything")

    def can_be_merged(self, _other: 'QueryAst') -> bool:  # pylint: disable=no-self-use
        return False


class QueryBiStatement(QueryAst, ABC):

    _statement_type: StatementType = None
    _provide_merge_for: Set[StatementType] = None

    @lazy
    def left(self) -> QueryAst:
        return prettify_value(self._args[0])

    @lazy
    def right(self) -> QueryAst:
        return prettify_value(self._args[1])

    @property
    def statement_type(self) -> StatementType:
        return self._statement_type

    def __and__(self, other: QueryAst) -> QueryAst:
        if not isinstance(other, QueryBiStatement):
            raise TypeError(f"Currently, cannot apply and for QueryBiStatement with {other.__class__.__name__} query ast class")
        if self.can_be_merged(other):
            return self.merge(other)
        return QueryAndStatement(self, other)

    def can_be_merged(self, other: QueryAst) -> bool:
        return (
            isinstance(other, QueryBiStatement) and not self.complicated and
            not other.complicated and self.left.row_name == other.left.row_name
        )

    @abstractmethod
    def _merge_provider(self, other: 'QueryBiStatement') -> 'QueryBiStatement':
        pass

    def merge(self, other: 'QueryAst') -> 'QueryAst':
        if not isinstance(other, QueryBiStatement):
            raise TypeError(f"Currently, cannot merge QueryBiStatement with {other.__class__.__name__} query ast class")
        merge_provider_founded = False
        merge_result: QueryAst = None
        if other.statement_type in self._provide_merge_for:
            merge_result = self._merge_provider(other)
            merge_provider_founded = True
        elif self.statement_type in other._provide_merge_for:
            merge_result = other._merge_provider(self)
            merge_provider_founded = True
        if not merge_provider_founded:
            raise QueryBuildException("Cannot find merge provider!")
        if merge_result is None:
            return EmptyQueryStatement()
        return merge_result

    @property
    def complicated(self) -> bool:
        """
        Check if query statement has QueryRow on both leafs
        """
        return isinstance(self.right, QueryAst)

    def __str__(self) -> str:
        return f"{self.left} {self.statement_type.value} {self.right}"

    def __repr__(self) -> str:
        return str(self)


class EmptyQueryStatement(QueryAst):
    """
    Empty query statement, return on incompatable statements merge
    """

    def __and__(self, other):
        return self

    @property
    def complicated(self) -> bool:
        return False

    def can_be_merged(self, _other: 'QueryAst') -> bool:
        return True

    def merge(self, _other: 'QueryAst') -> 'QueryAst':
        return self

    def __str__(self) -> str:
        return '(empty set)'

    def __repl__(self) -> str:
        return str(self)


class QueryAndStatement(QueryAst):

    _args_order_important = False

    def __and__(self, other: QueryAst) -> QueryAst:
        if not isinstance(other, QueryBiStatement):
            raise TypeError(f"Currently, cannot merge QueryAndStatement with {other.__class__.__name__} query ast class")
        merge_candidate: QueryBiStatement = next(filter(lambda statement: statement.can_be_merged(other), self._args), None)
        if merge_candidate is not None:
            self._args[self._args.index(merge_candidate)] = merge_candidate.merge(other)
        else:
            self._args.append(other)
        return self

    @property
    def complicated(self) -> bool:
        return True

    def __str__(self) -> str:
        return ' & '.join(map(str, self._args))

    def __repl__(self) -> str:
        return self.__str__()


class QueryEqualStatement(QueryBiStatement):

    _statement_type = StatementType.eq
    _args_order_important = False
    _provide_merge_for = {
        StatementType.ne, StatementType.eq, StatementType.bound, StatementType.ge,
        StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBiStatement) -> QueryBiStatement:
        compitability_check = (
            (other.statement_type == StatementType.eq and other.right == self.right) or
            (other.statement_type in [StatementType.isin, StatementType.bound] and self.right in other.right) or
            (other.statement_type == StatementType.lt and self.right < other.right) or
            (other.statement_type == StatementType.le and self.right <= other.right) or
            (other.statement_type == StatementType.ge and self.right >= other.right) or
            (other.statement_type == StatementType.gt and self.right > other.right) or
            (other.statement_type == StatementType.ne and self.right != other.right)
        )
        return self if compitability_check else None


class QueryGreaterOrEqualStatement(QueryBiStatement):

    _statement_type = StatementType.ge
    _provide_merge_for = {
        StatementType.ge, StatementType.gt
    }

    def _merge_provider(self, other: QueryBiStatement) -> QueryBiStatement:
        if self.right > other.right:
            return self
        return other


class QueryGreaterStatement(QueryBiStatement):

    _statement_type = StatementType.gt
    _provide_merge_for = {
        StatementType.gt
    }

    def _merge_provider(self, other: QueryBiStatement) -> QueryBiStatement:
        if self.right > other.right:
            return self
        return other


class QueryLowerOrEqualStatement(QueryBiStatement):

    _statement_type = StatementType.le
    _provide_merge_for = {
        StatementType.ge, StatementType.le, StatementType.lt, StatementType.gt
    }

    def _merge_provider(self, other: QueryBiStatement) -> QueryBiStatement:
        if other.statement_type in [StatementType.le, StatementType.lt]:
            if self.right < other.right:
                return self
            return other
        if self.right >= other.right:
            return QueryBoundStatement(
                self.left,
                Interval(
                    other.right, self.right,
                    left_close=other.statement_type == StatementType.ge, right_close=True
                )
            )
        return None


class QueryLowerStatement(QueryBiStatement):

    _statement_type = StatementType.lt
    _provide_merge_for = {
        StatementType.ge, StatementType.lt, StatementType.gt
    }

    def _merge_provider(self, other: QueryBiStatement) -> QueryBiStatement:
        if other.statement_type == StatementType.lt:
            if self.right < other.right:
                return self
            return other
        if self.right >= other.right:
            return QueryBoundStatement(
                self.left,
                Interval(
                    other.right, self.right,
                    left_close=other.statement_type == StatementType.ge, right_close=False
                )
            )
        return None


class QueryNotEqualStatement(QueryBiStatement):

    _statement_type = StatementType.ne
    _args_order_important = False
    _provide_merge_for = {
        StatementType.ne, StatementType.eq, StatementType.bound, StatementType.ge,
        StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBiStatement) -> QueryBiStatement:
        compitability_check = (
            (other.statement_type == StatementType.eq and other.right == self.right) or
            (other.statement_type in [StatementType.isin, StatementType.bound] and self.right in other.right) or
            (other.statement_type == StatementType.lt and self.right < other.right) or
            (other.statement_type == StatementType.le and self.right <= other.right) or
            (other.statement_type == StatementType.ge and self.right >= other.right) or
            (other.statement_type == StatementType.gt and self.right > other.right) or
            (other.statement_type == StatementType.ne and self.right != other.right)
        )
        if not compitability_check:
            return other
        elif other.statement_type == StatementType.isin:
            new_elements = tuple(x for x in other.right if x != self.right)
            if new_elements:
                return QueryContainsStatement(self.left, new_elements)
        elif other.statement_type == StatementType.bound:
            if self.right in other.right:
                _log.warning("Currently, bound statement cannot be merged with ne statement, so just ingore ne statement")
            return other
        return None


class QueryContainsStatement(QueryBiStatement):

    _statement_type = StatementType.isin
    _provide_merge_for = {
        StatementType.ge, StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBiStatement) -> QueryBiStatement:
        if other.statement_type == StatementType.isin:
            intersection = tuple(x for x in self.right if x in other.right)
            if intersection:
                return QueryContainsStatement(self.left, intersection)
            return None
        method_name = f"__{other.statement_type.name}__"
        for element in self.right:
            if not getattr(element, method_name)(other.right):
                return None
        return self


class QueryBoundStatement(QueryBiStatement):

    _statement_type = StatementType.bound
    _provide_merge_for = {
        StatementType.bound, StatementType.ge,
        StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBiStatement) -> QueryBiStatement:
        if other.statement_type == StatementType.isin:
            for element in other.right:
                if element not in self.right:
                    return None
            return other
        interval = self.right.clone()
        # Convert to QueryBoundStatement to make same codebase for many statement type
        # If you want to change it, make sure that all types covered
        if other.statement_type in [StatementType.le, StatementType.lt]:
            interval.right_close = other.statement_type == StatementType.le
            interval.right_bound = other.right
            other = QueryBoundStatement(self.left, interval)
        if other.statement_type in [StatementType.ge, StatementType.gt]:
            interval.left_close = other.statement_type == StatementType.ge
            interval.left_bound = other.right
            other = QueryBoundStatement(self.left, interval)
        if other.statement_type == StatementType.bound:
            interval = other.right
        if interval.valid:
            if self.right.contains_interval(interval):
                return other
            if interval.contains_interval(self.right):
                return self
        return None


class QueryRow(QueryAst):

    @property
    def row_name(self):
        return self._args[0]

    def one_of(self, *variants) -> QueryBiStatement:
        return QueryContainsStatement(self, variants)

    def contains(self, another_row: 'QueryRow') -> QueryBiStatement:
        return QueryContainsStatement(another_row, self)

    def __eq__(self, other) -> QueryBiStatement:  # type: ignore
        return QueryEqualStatement(self, other)

    def __ge__(self, other) -> QueryBiStatement:
        return QueryGreaterOrEqualStatement(self, other)

    def __gt__(self, other) -> QueryBiStatement:
        return QueryGreaterStatement(self, other)

    def __ne__(self, other) -> QueryBiStatement:  # type: ignore
        return QueryNotEqualStatement(self, other)

    def __lt__(self, other) -> QueryBiStatement:
        return QueryLowerStatement(self, other)

    def __le__(self, other) -> QueryBiStatement:
        return QueryLowerOrEqualStatement(self, other)

    def __str__(self) -> str:
        return f"row[{self._args[0]}]"
