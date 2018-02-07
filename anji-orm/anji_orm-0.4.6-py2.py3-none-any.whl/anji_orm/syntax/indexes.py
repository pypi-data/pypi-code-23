import abc
from itertools import combinations
from typing import List, Tuple, Sequence

import rethinkdb as R

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.4.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['AbstractIndexPolicy', 'GreedyIndexPolicy', 'SingleIndexPolicy']


class AbstractIndexPolicy(abc.ABC):

    """
    Abstract class for policies, that can be used to work with indexes.
    Policy works like strategy pattern.
    """

    @classmethod
    @abc.abstractmethod
    def build_secondary_index_list(cls, secondary_indexes_fields: List[str]) -> List[str]:
        """
        Define a way how to build secondary indexes based on fields that was marked
        as secondary index

        :param secondary_indexes_fields: List of fields that was marked as secondary indexes
        :return: secondary index list
        """

    @classmethod
    def index_creation_query(cls, secondary_index_name: str, table_name: str) -> R.RqlQuery:
        """
        Define a way how to build secondary indexes based on name.
        Basically, two simple rules:
        1. When name without ':' just create index by field that named same as :any:`secondary_index_name`
        2. If name has ':', split on it and create complex index.

        So, for index 'catman' create RethinkDB index on field 'catman'.
        And for index 'catman:mercuria', create compound index on fields 'catman' and 'mercuria'.

        .. seealso:: RethinkDB `documentation <https://www.rethinkdb.com/docs/secondary-indexes/python/>` about indexes

        :param secondary_index_name: secondary index name
        :param table_name: name of target table
        :return: Query to build this index in RethinkDB
        """
        if ':' not in secondary_index_name:
            return R.table(table_name).index_create(secondary_index_name)
        return R.table(table_name).index_create(
            secondary_index_name,
            [R.row[x] for x in secondary_index_name.split(':')]
        )

    @classmethod
    @abc.abstractmethod
    def select_secondary_index(cls, secondary_indexes_fields: List[str]) -> Tuple[str, Sequence[str]]:
        """
        Define that way how to select secondary index for query.

        :param secondary_indexes_fields: Fields that used in query
        :return: (selected index, unused elements)
        """
        pass  # pragma: no cover


class GreedyIndexPolicy(AbstractIndexPolicy):

    """
    Simple index policy based on greedy logic.
    So, that means create index for any field and any field combination.
    For example. model with two indexed fields 'cat' and 'dog' will produce three indexes:
    - cat
    - dog
    - cat:dog
    """

    @classmethod
    def build_secondary_index_list(cls, secondary_indexes_fields: List[str]) -> List[str]:
        """
        Procude index for every field and any field combinations

        :param secondary_indexes_fields: List of fields that was marked as secondary indexes
        :return: secondary index list
        """
        secondary_indexes = []
        secondary_indexes.extend(secondary_indexes_fields)
        secondary_indexes_fields = sorted(secondary_indexes_fields)
        for combination_size in range(2, len(secondary_indexes_fields)):
            secondary_indexes.extend(
                (':'.join(x) for x in combinations(secondary_indexes_fields, combination_size))
            )
        secondary_indexes.append(":".join(secondary_indexes_fields))
        return secondary_indexes

    @classmethod
    def select_secondary_index(cls, secondary_indexes_fields: List[str]) -> Tuple[str, Sequence[str]]:
        """
        Select index based on all fields

        :param secondary_indexes_fields: Fields that used in query
        :return: (selected index, empty tuple)
        """
        return ':'.join(sorted(secondary_indexes_fields)), ()


class SingleIndexPolicy(AbstractIndexPolicy):

    """
    Simple index policy based on clear logic.
    So, that means create index for any field and no field combination.
    For example. model with two indexed fields 'cat' and 'dog' will produce only two indexes:
    - cat
    - dogs
    """

    @classmethod
    def build_secondary_index_list(cls, secondary_indexes_fields: List[str]) -> List[str]:
        """
        Procude index for every field and no field combinations

        :param secondary_indexes_fields: List of fields that was marked as secondary indexes
        :return: same as :any:`secondary_indexes_fields` variable
        """
        return secondary_indexes_fields

    @classmethod
    def select_secondary_index(cls, secondary_indexes_fields: List[str]) -> Tuple[str, Sequence[str]]:
        """
        Select index based on first fields

        :param secondary_indexes_fields: Fields that used in query
        :return: (first field, rest fields)
        """
        return secondary_indexes_fields[0], secondary_indexes_fields[1:]
