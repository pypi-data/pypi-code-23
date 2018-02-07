import unittest
import pandas as pd

from vaquero.transformations import *


class TestTransformations(unittest.TestCase):

    def test_robust_float(self):
        self.assertEqual(robust_float(1), 1.0)
        self.assertEqual(robust_float(1.5), 1.5)
        self.assertEqual(robust_float("1"), 1)
        self.assertEqual(robust_float("1.5"), 1.5)
        self.assertEqual(robust_float("$27,182,818.28"), 27182818.28)
        self.assertIsNone(robust_float("bird"))
        self.assertIsNone(robust_float(None))

    def test_robust_int(self):
        self.assertEqual(robust_int(1), 1)
        self.assertEqual(robust_int(1.5), 1)
        self.assertEqual(robust_int("1"), 1)
        self.assertEqual(robust_int("1.5"), 1)
        self.assertEqual(robust_int("$27,182,818.28"), 27182818)
        self.assertIsNone(robust_float("bird"))
        self.assertIsNone(robust_float(None))

    def test_rename_ks(self):
        d = {'a': 10, 'b': 20}
        expected = {'A': 10, 'b_': 20}
        rename_ks(d, {'a': 'A', 'b': 'b_'})
        self.assertEqual(d, expected)

        with self.assertRaisesRegexp(AssertionError, 'not in'):
            d = {'a': 10, 'b': 20}
            rename_ks(d, {'a': 'A', 'b': 'b_', 'c': 'C'}, must_exist=True)

    def test_fill_in_unknowns(self):
        a = {'name': {'first': "John"}, 'age': -1}
        b = {'name': {'last': "Nelson"}, 'age': 32}
        expected = {'name': {'first': "John", 'last': "Nelson"}, 'age': -1}

        doc = {}
        fill_in_unknowns(a, doc)
        fill_in_unknowns(b, doc)
        self.assertEqual(doc, expected)

    def test_dict_values_to_int(self):
        d = {'x': 100, 'y': ' 200 '}
        expected = {'x': 100, 'y': 200}
        dict_values_to_int(d, ['x', 'y', 'z'])
        self.assertEqual(d, expected)

        with self.assertRaisesRegexp(AssertionError, 'not in'):
            dict_values_to_int(d, ['x', 'y', 'z'], must_exist=True)

    def test_dict_values_to_float(self):
        d = {'x': 100.5, 'y': ' 200.3 '}
        expected = {'x': 100.5, 'y': 200.3}
        dict_values_to_float(d, ['x', 'y', 'z'])
        self.assertEqual(d, expected)

    def test_dict_string_values_to_bool(self):
        d = {'x': 'YES', 'y': 'no', 'z': '-'}

        expected = {'x': True, 'y': False, 'z': None}
        dict_string_values_to_bool(d, ['x', 'y', 'z'])
        self.assertEqual(d, expected)

    def test_sstrip(self):
        s = "   hello hello why     don't \t\t\tyou come right in    \t\n"
        expected = "hello hello why don't you come right in"
        self.assertEqual(sstrip(s), expected)

    def test_sstrip_all(self):
        items = ["  a\tb   ", "c\t\td"]
        sstrip_all(items)
        self.assertEqual(items, ["a b", "c d"])

    def test_pythonize_identifier(self):
        example = pythonize_identifier("$InCONSISTENTCY is f*#$#g FUN :)")
        expected = "inconsistentcy_is_f_g_fun"
        self.assertEqual(pythonize_identifier(example), expected)

        self.assertEqual(pythonize_identifier(""), "")

        self.assertEqual(pythonize_identifier("$"), "")

    def test_pythonize_keys(self):
        example = {'first$name': "John",
                   'last.name': "Nelson",
                   'location': {'city a': "NYC", 'city b': "LA"}}
        pythonize_ks(example)
        self.assertEqual(example,
                         {'first_name': 'John',
                          'last_name': 'Nelson',
                          'location': {'city_a': 'NYC', 'city_b': 'LA'}})

        example = {"owner's number": 42}
        pythonize_ks(example, delete_chars="'")
        self.assertEqual(example, {"owners_number": 42})

    def test_dict_values_to_upper_if_str(self):
        example = {'a': "john", 'b': 32}
        dict_values_to_upper_if_str(example)
        self.assertEqual(example, {'a': "JOHN", 'b': 32})

    def test_flat_mapping_of_dict(self):
        example = {'billing': {'address': "42 main street", 10: 'something'}}
        result = flat_mapping_of_dict(example, sep='-')
        self.assertEqual(result, {'billing-address': "42 main street",
                                  'billing-10': "something"})

    def test_remove_private_keys(self):
        example = {'-a': 20, 'b': {'-c': 100, 'd': 300}}
        expected = {'b': {'d': 300}}
        remove_private_keys(example, prefix='-')
        self.assertEqual(example, expected)

    def test_reindex_columns_partial(self):
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3], 'z': [1, 2, 3]})
        self.assertTrue(all(df.columns == ['x', 'y', 'z']))
        df_1 = reindex_columns_partial(df, ['z', 'x', 'y'])
        self.assertTrue(all(df_1.columns == ['z', 'x', 'y']))
        self.assertTrue(all(df.columns == ['x', 'y', 'z']))
        with self.assertRaisesRegexp(KeyError, "keys"):
            reindex_columns_partial(df, ['w'])
