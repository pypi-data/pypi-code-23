import unittest

from anji_orm.syntax.query import Interval


class IntervalTest(unittest.TestCase):

    def test_interval_contains(self):
        self.assertTrue(5 in Interval(4, 6))
        self.assertTrue(5 in Interval(4, 5, right_close=True))
        self.assertTrue(5 in Interval(5, 6, left_close=True))
        self.assertTrue(5 not in Interval(4, 5))
        self.assertTrue(5 not in Interval(7, 8))

    def test_internal_contains_interval(self):
        self.assertTrue(Interval(3, 7).contains_interval(Interval(4, 6)))
        self.assertTrue(Interval(4, 7).contains_interval(Interval(4, 6)))
        self.assertTrue(Interval(3, 6).contains_interval(Interval(4, 6)))

        self.assertFalse(Interval(4, 6).contains_interval(Interval(3, 7)))
        self.assertFalse(Interval(4, 6).contains_interval(Interval(4, 7)))
        self.assertFalse(Interval(4, 6).contains_interval(Interval(3, 6)))

        self.assertTrue(Interval(4, 7, left_close=True).contains_interval(Interval(4, 6)))
        self.assertFalse(Interval(4, 7).contains_interval(Interval(4, 6, left_close=True)))
        self.assertTrue(Interval(4, 7, right_close=True).contains_interval(Interval(5, 7)))
        self.assertFalse(Interval(4, 7).contains_interval(Interval(5, 7, right_close=True)))

    def test_internal_with_not_interval(self):
        self.assertNotEqual(Interval(3, 5), '5')
        self.assertNotEqual(Interval(3, 5), 5)
        self.assertNotEqual(Interval(3, 5), self)

    def test_convertation_to_string(self):
        self.assertEqual(str(Interval(3, 5)), '(3, 5)')
        self.assertEqual(str(Interval(3, 5, left_close=True)), '[3, 5)')
        self.assertEqual(str(Interval(3, 5, right_close=True)), '(3, 5]')
        self.assertEqual(str(Interval(3, 5, left_close=True, right_close=True)), '[3, 5]')

    def test_is_valid(self):
        self.assertTrue(Interval(3, 5).valid)
        self.assertTrue(Interval(3, 5, left_close=True).valid)
        self.assertTrue(Interval(3, 5, right_close=True).valid)
        self.assertTrue(Interval(3, 5, left_close=True, right_close=True).valid)
        self.assertTrue(Interval(3, 3, left_close=True, right_close=True).valid)
        self.assertFalse(Interval(3, 3, left_close=True).valid)
        self.assertFalse(Interval(3, 3, right_close=True).valid)
        self.assertFalse(Interval(3, 3).valid)
        self.assertFalse(Interval(5, 3).valid)
