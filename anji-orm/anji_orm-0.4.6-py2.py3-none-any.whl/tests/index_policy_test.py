import unittest
from itertools import combinations

import rethinkdb as R
from hypothesis import given, strategies as st

from anji_orm.syntax.indexes import AbstractIndexPolicy, SingleIndexPolicy, GreedyIndexPolicy

from .base import BaseTestCase


function_name = st.text(
    st.characters(min_codepoint=97, max_codepoint=122, whitelist_characters=('_', '2')),
    min_size=5
)


class AbstractIndexPolicyTest(BaseTestCase):

    @given(
        function_name,
        function_name
    )
    def test_simple_index_creation(self, table_name, index_name):
        print(table_name, index_name)
        target_query = R.table(table_name).index_create(index_name)
        result_query = AbstractIndexPolicy.index_creation_query(index_name, table_name)
        self.assertQueryEqual(target_query, result_query)

    @given(
        function_name,
        function_name,
        st.lists(function_name, min_size=1, average_size=2, max_size=5)
    )
    def test_compound_index_creation(self, table_name, first_index_name, rest_indexes):
        index_name = f"{first_index_name}:{':'.join(rest_indexes)}"
        index_fields = [R.row[index_name]]
        for index in rest_indexes:
            index_fields.append(R.row[index])
        target_query = R.table(table_name).index_create(
            index_name,
            index_fields
        )
        result_query = AbstractIndexPolicy.index_creation_query(index_name, table_name)
        self.assertQueryEqual(target_query, result_query)


class SingleIndexPolicyTest(unittest.TestCase):

    @given(
        st.lists(function_name, min_size=1, average_size=3, max_size=5)
    )
    def test_single_build_index(self, index_list):
        self.assertEqual(
            index_list,
            SingleIndexPolicy.build_secondary_index_list(index_list)
        )

    @given(
        st.lists(function_name, min_size=1, average_size=3, max_size=5)
    )
    def test_single_select_index(self, index_list):
        selected_index, unused_indexes = SingleIndexPolicy.select_secondary_index(index_list)
        self.assertEqual(selected_index, index_list[0])
        self.assertEqual(unused_indexes, index_list[1:])


class GreedyIndexPolicyTest(unittest.TestCase):

    @given(
        st.lists(function_name, min_size=1, average_size=3, max_size=5)
    )
    def test_greedy_build_index(self, index_list):
        builded_index_list = GreedyIndexPolicy.build_secondary_index_list(index_list)
        target_index_list = []
        target_index_list.extend(index_list)
        index_list = sorted(index_list)
        for combination_size in range(2, len(index_list)):
            target_index_list.extend(
                (':'.join(x) for x in combinations(index_list, combination_size))
            )
        target_index_list.append(":".join(index_list))
        self.assertEqual(target_index_list, builded_index_list)

    @given(
        st.lists(function_name, min_size=1, average_size=3, max_size=5)
    )
    def test_greedy_select_index(self, index_list):
        selected_index, unused_indexes = GreedyIndexPolicy.select_secondary_index(index_list)
        self.assertEqual(selected_index, ":".join(sorted(index_list)))
        self.assertEqual(unused_indexes, ())
