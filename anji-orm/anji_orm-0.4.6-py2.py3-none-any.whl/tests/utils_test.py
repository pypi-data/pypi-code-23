import asyncio
import unittest
from enum import Enum

import asynctest
import rethinkdb as R

from anji_orm.utils import ensure_element, prettify_value, check_equals


class NotPrettyEnum(Enum):

    first = 'first'
    second = 'second'
    haha = 'haha'


class PrettifyValueTest(unittest.TestCase):

    def test_prettify_value_for_dict(self):
        base_dict = {
            "t1": 5,
            "t2": '3'
        }
        test_dict = base_dict.copy()
        target_dict = base_dict.copy()
        test_dict['t3'] = NotPrettyEnum.first
        target_dict['t3'] = NotPrettyEnum.first.name
        self.assertEqual(prettify_value(test_dict), target_dict)

    def test_prettify_value_for_list(self):
        base_list = [5, '3']
        test_list = base_list[:]
        target_list = base_list[:]
        test_list.append(NotPrettyEnum.second)
        target_list.append(NotPrettyEnum.second.name)
        self.assertEqual(prettify_value(test_list), target_list)

    def test_prettify_value_for_tuple(self):
        base_tuple = (5, '3')
        test_tuple = base_tuple + (NotPrettyEnum.haha,)
        target_tuple = base_tuple + (NotPrettyEnum.haha.name,)
        self.assertEqual(prettify_value(test_tuple), target_tuple)

    def test_prettify_value_for_enum(self):
        self.assertEqual(prettify_value(NotPrettyEnum.first), NotPrettyEnum.first.name)


class QueryCompareTest(unittest.TestCase):

    def simple_test(self):
        self.assertTrue(
            check_equals(
                R.table('non_table').filter(R.row['t1'] == 't2').limit(5).count(6),
                R.table('non_table').filter(R.row['t1'] == 't2').limit(5).count(6)
            )
        )

        self.assertTrue(
            check_equals(
                R.table('non_table').filter(lambda doc: doc.match('5')).limit(5).count(6),
                R.table('non_table').filter(lambda doc: doc.match('5')).limit(5).count(6)
            )
        )

        self.assertTrue(
            check_equals(
                R.table('non_table').get_all('a1', 'a2', index='c2').filter(lambda doc: R.expr(['a1', 'a2']).contains(doc['c3'])),
                R.table('non_table').get_all('a1', 'a2', index='c2').filter(lambda doc: R.expr(['a1', 'a2']).contains(doc['c3']))
            )
        )

        self.assertTrue(
            check_equals(
                R.table('non_table').filter((R.row['c1'] >= 5) & (R.row['c2'] <= 6)),
                R.table('non_table').filter((R.row['c2'] <= 6) & (R.row['c1'] >= 5))
            )
        )


class EnsureElementTest(asynctest.TestCase):

    def setUp(self):
        self.value = '5'
        self.value_list = ['5', 6, 75]
        self.value_dict = {
            't1': ['t5', 't7'],
            't2': 5,
            6: '57'
        }

    async def gen_value(self):
        return self.value

    async def gen_value_list(self):
        return self.value_list

    async def gen_value_dict(self):
        return self.value_dict

    def gen_value_list_of_dicts(self, loop):
        return [
            loop.create_task(self.gen_value_dict()),
            loop.create_task(self.gen_value_dict()),
            self.value_dict,
            self.value
        ]

    def gen_value_dict_with_lists(self, loop):
        return {
            1: loop.create_task(self.gen_value_list()),
            2: loop.create_task(self.gen_value_list()),
            3: self.value_list,
            4: self.value
        }

    def get_value_dict_with_dicts(self, loop):
        return {
            1: loop.create_task(self.gen_value_list()),
            2: loop.create_task(self.gen_value_dict()),
            3: self.value_list,
            4: self.value
        }

    async def test_simple_no_await(self):
        self.assertEqual(self.value, await ensure_element(self.value))

    async def test_simple_no_await_list(self):
        self.assertEqual(self.value_list, await ensure_element(self.value_list))

    async def test_simple_no_await_dict(self):
        self.assertEqual(self.value_dict, await ensure_element(self.value_dict))

    async def test_simple_await(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(self.value, await ensure_element(loop.create_task(self.gen_value())))

    async def test_simple_list(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(self.value_list, await ensure_element(loop.create_task(self.gen_value_list())))

    async def test_simple_dict(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(self.value_dict, await ensure_element(loop.create_task(self.gen_value_dict())))

    async def test_dict_in_list(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(
            [self.value_dict, self.value_dict, self.value_dict, self.value],
            await ensure_element(self.gen_value_list_of_dicts(loop))
        )

    async def test_list_in_dict(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(
            {1: self.value_list, 2: self.value_list, 3: self.value_list, 4: self.value},
            await ensure_element(self.gen_value_dict_with_lists(loop))
        )

    async def test_dict_in_dict(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(
            {1: self.value_list, 2: self.value_dict, 3: self.value_list, 4: self.value},
            await ensure_element(self.get_value_dict_with_dicts(loop))
        )
