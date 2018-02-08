import unittest

from vaquero.collectors import *


class TestSetCollector(unittest.TestCase):
    def test_sampling(self):
        # This test fails stochastically, once every 50,000 times.
        k = len(list(sampling(range(100), 0.2)))
        self.assertGreaterEqual(k, 5)
        self.assertLessEqual(k, 38)

    def test_collector(self):
        collector = Collector()
        with self.assertRaises(NotImplementedError):
            collector.update(42)

        with self.assertRaises(NotImplementedError):
            collector.collected

    def test_set_collector(self):
        docs = [{'name': "John", "props": {'sex': "M"}},
                {'name': "Kim", "props": {'sex': "F"}},
                {'is_missing': "YES"}]
        set_collector = SetCollector(["name", "props.sex"])
        set_collector.update_over_all(docs)

        self.assertEqual(set_collector.collected,
                         {'name': {"John", "Kim"},
                          'props.sex': {"F", "M"}})

    def test_group_collector(self):
        docs = [1, 2, 3, 4]
        collector = GroupCollector(lambda item: item % 2)
        collector.update_over_all(docs)
        self.assertEqual(collector.collected, {0: 2, 1: 1})
