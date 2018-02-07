import unittest

from typing import Any, List  # NOQA

import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from edpanalyst.guess import (ColumnDefinition, guess_schema,
                              make_column_from_hint, _guess_precision)


class TestGuess(unittest.TestCase):

    def test_basic_schema(self):  # type: () -> None
        rs = np.random.RandomState(17)
        test_frame = pd.DataFrame.from_items([
            ('few_numbers', [rs.randint(0, 10) for _ in range(100)]),
            ('more_numbers', [rs.randint(0, 100) for _ in range(100)]),
            ('all_distinct_numbers', [i for i in range(100)]),
            ('all_distinct_strings', [('val' + str(i)) for i in range(100)]),
            ('constant', [1 for _ in range(100)]),
        ])
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'few_numbers',
                    'stat_type': 'orderedCategorical',
                    'values': [{'value': str(x)} for x in range(10)],
                    'stat_type_reason': 'Only 10 distinct values'
                },
                {
                    'name': 'more_numbers',
                    'stat_type': 'realAdditive',
                    'stat_type_reason':
                    'Contains only numbers (68 of them, uniform cor. 0.997, '
                    'log-uniform cor. 0.866)',
                    'precision': [1, 1],
                },
                {
                    'name': 'all_distinct_numbers',
                    'stat_type': 'realAdditive',
                    'stat_type_reason':
                    'Contains only numbers (100 of them, uniform '
                    'cor. 1.000, log-uniform cor. 0.896)',
                    'precision': [1, 1],
                },
                {
                    'name': 'all_distinct_strings',
                    'stat_type': 'void',
                    'stat_type_reason': 'Non-numeric and all values unique'
                },
                {
                    'name': 'constant',
                    'stat_type': 'void',
                    'stat_type_reason': 'Column is constant'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_tricky_categoricals(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items(
            [('foo', [.1, 1.000000002, float('nan'), ""])])
        guessed = guess_schema(test_frame).to_json()
        # NaN doesn't count, but empty string does
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': ''},
                        {'value': '0.1'},
                        {'value': '1.000000002'},
                    ],
                    'stat_type_reason': 'Only 3 distinct values'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_categorical_value_sorting(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items(
            [('foo', [0, 1, 'A', 'c', 2, 100, 'B', 20, 'IMASTRING', 'AA',
                      10])])
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': '0'},
                        {'value': '1'},
                        {'value': '2'},
                        {'value': '10'},
                        {'value': '20'},
                        {'value': '100'},
                        {'value': 'A'},
                        {'value': 'AA'},
                        {'value': 'B'},
                        {'value': 'c'},
                        {'value': 'IMASTRING'},
                    ],
                    'stat_type_reason': 'Only 11 distinct values'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_too_sparse_categorical(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items(
            [('foo', ["f{}".format(x) for x in range(100)] * 2)])
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'void',
                    'stat_type_reason': '100 distinct values. 100 are '
                                        'non-numeric (f0, f1, f2, ...)'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_one_non_number_and_null(self):  # type: () -> None
        vals = list(range(30))  # type: List[Any]
        vals = vals + ['-', np.nan]
        test_frame = pd.DataFrame.from_dict({'foo': vals})
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'void',
                    'stat_type_reason':
                        '31 distinct values. 1 are non-numeric (-)'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_poorly_covered_categorical(self):  # type: () -> None
        vals = [('s' + str(x)) for x in list(range(30))]  # type: List[Any]
        vals = [None] + vals
        test_frame = pd.DataFrame.from_dict({'foo': vals})
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'void',
                    'stat_type_reason': '30 distinct values. 30 are '
                                        'non-numeric (s0, s1, s2, ...)'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_ordered_categorical(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items([('foo', [4, 3.0, 1, 7, 2, 5])])
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'orderedCategorical',
                    'values': [
                        {'value': '1.0'},
                        {'value': '2.0'},
                        {'value': '3.0'},
                        {'value': '4.0'},
                        {'value': '5.0'},
                        {'value': '7.0'},
                    ],
                    'stat_type_reason': 'Only 6 distinct values'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_trickier_ordered_categorical(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items(
            [('foo', ['3-7', '1-3 doctors', '7-29'])])
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'orderedCategorical',
                    'values': [
                        {'value': '1-3 doctors'},
                        {'value': '3-7'},
                        {'value': '7-29'},
                    ],
                    'stat_type_reason': 'Only 3 distinct values'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_normal_transformation(self):  # type: () -> None
        # Check that normal and lognormal data with the same mean and variance
        # get classified as realAdditive and realMultiplicative, respectively.
        # This isn't a great test; Madeleine doesn't think you can really ever
        # find a normal distribution with the same mean and variance as a
        # lognormal distribution where both don't fit about as well as each
        # other unless the normal distribution has negative numbers.

        # Generate some random data.
        n = 1000
        rs = np.random.RandomState(17)
        lognormal_data = rs.lognormal(1.2, 0.8, size=n)
        normal_data = rs.normal(
            np.mean(lognormal_data), np.std(lognormal_data), size=n)
        test_frame = pd.DataFrame.from_items([('normal', normal_data),
                                              ('log_normal', lognormal_data)])

        # Check that `guess_schema` guesses correctly.
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [
                {'name': 'normal', 'stat_type': 'realAdditive'},
                {'name': 'log_normal', 'stat_type': 'realMultiplicative'},
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_log_normal_with_single_negative_value(self):  # type: () -> None
        rs = np.random.RandomState(17)
        data = rs.lognormal(0, 1, 10000)
        data = np.append(data, -.01)
        test_frame = pd.DataFrame({'almost_log_normal': data})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        # It's not actually for sure true that this should be realAdditive and
        # not realMultiplicative. See the discussion in guess.py.
        expected = {
            'columns': [{
                'name': 'almost_log_normal',
                'stat_type': 'realAdditive'
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_log_normal_with_lotsa_zeros(self):  # type: () -> None
        rs = np.random.RandomState(17)
        data = rs.lognormal(0, 1, 10000)
        data = np.append(data, [0] * 1000)
        test_frame = pd.DataFrame({'almost_log_normal': data})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'almost_log_normal',
                'stat_type': 'magnitude'
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_numeric_column_full_of_strings(self):  # type: () -> None
        rs = np.random.RandomState(17)
        test_frame = pd.DataFrame({
            'str_numbers': [str(rs.randint(0, 100)) for _ in range(100)]
        })
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'str_numbers',
                'stat_type': 'realAdditive',
                'precision': [1, 1],
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_numeric_column_of_thousands(self):  # type: () -> None
        rs = np.random.RandomState(17)
        test_frame = pd.DataFrame({
            'th': [1000 * rs.randint(-50, 50) for _ in range(100)]
        })
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'th',
                'stat_type': 'realAdditive',
                'precision': [1000, 1],
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_multiplicative_column_of_tenths(self):  # type: () -> None
        rs = np.random.RandomState(17)
        tenths = np.round(np.exp(rs.normal(2, 1, size=100)), decimals=1)
        test_frame = pd.DataFrame({'tenths': tenths})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'tenths',
                'stat_type': 'realMultiplicative',
                'precision': [1, 10],
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_guess_precision(self):  # type: () -> None
        # Try units of 1000, 100, ..., 0.01 and confirm they're guessed. We
        # can't use subTest in this test because it's python3-only.
        rng = np.random.RandomState(17)
        for places in range(-3, 3):
            x = rng.randint(-1e6, 1e6, size=1000) / 10**places
            prec = _guess_precision(x)
            if places <= 0:
                self.assertEqual((10**-places, 1), prec)
            else:
                self.assertEqual((1, 10**places), prec)

    def test_precision_when_all_bits_are_used(self):  # type: () -> None
        rng = np.random.RandomState(17)
        self.assertIsNone(_guess_precision(rng.normal(0, 1, size=100)))

    def test_precision_on_very_large_integers(self):  # type: () -> None
        rng = np.random.RandomState(17)
        self.assertIsNone(_guess_precision(rng.randint(1e15, size=100)))

    def test_precision_on_very_small_fractions(self):  # type: () -> None
        self.assertIsNone(_guess_precision(np.array([1e-30, 3e-30, 2e-30])))

    def test_pandas_timestamps(self):  # type: () -> None
        dates = pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03'])
        test_frame = pd.DataFrame({'x': dates})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'x',
                'stat_type': 'date',
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_date_strings(self):  # type: () -> None
        test_frame = pd.DataFrame({
            'x': ['2017-01-01', '2017-01-02', '2017-01-03']
        })
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'x',
                'stat_type': 'date',
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_times_are_not_guessed_to_be_dates(self):  # type: () -> None
        self.maxDiff = None
        time_strings = ['2017-01-01 12:34:56', '2017-01-02 12:34:56']
        data = pd.DataFrame({
            'x1': pd.to_datetime(time_strings),
            'x2': time_strings,
        })
        guessed = guess_schema(data).to_json(drop_reasons=True)
        expected = {
            'columns': [
                {
                    'name': 'x1',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': v} for v in data['x1'].unique().astype(str)
                    ],
                },
                {
                    'name': 'x2',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': time_strings[0]},
                        {'value': time_strings[1]},
                    ],
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)


class TestHint(unittest.TestCase):

    def test_no_stat_type(self):
        with self.assertRaises(ValueError):
            make_column_from_hint('foo', pd.Series([1, 2, 3]), {
                'invalid': 'hint'
            })

    def test_void_hint(self):
        old_values = pd.Series(['total', 1, 'junk'])
        column_definition = make_column_from_hint('junk', old_values, {
            'stat_type': 'void'
        })

        self.assertEqual(column_definition,
                         ColumnDefinition('junk', 'void', 'Hinted'))

    def test_categorical_hints(self):
        column_definition = make_column_from_hint(
            'actually_categorical', pd.Series([1, 2, 3]), {
                'stat_type': 'categorical'
            })

        self.assertEqual(column_definition,
                         ColumnDefinition('actually_categorical',
                                          'categorical', 'Hinted',
                                          values=['1', '2', '3']))

    def test_numeric_hints(self):
        column_definition = make_column_from_hint(
            'actually_numeric', pd.Series(['1', '2', '3']), {
                'stat_type': 'realMultiplicative'
            })

        self.assertEqual(column_definition,
                         ColumnDefinition('actually_numeric',
                                          'realMultiplicative', 'Hinted',
                                          precision=(1, 1)))

    def test_general_numeric_hints(self):
        column_definition = make_column_from_hint('actually_numeric',
                                                  pd.Series(['1', '2', '3']), {
                                                      'stat_type': 'real'
                                                  })

        self.assertEqual(column_definition,
                         ColumnDefinition('actually_numeric', 'realAdditive',
                                          'Hinted', precision=(1, 1)))

    def test_numeric_hint_problem(self):
        with self.assertRaises(ValueError):
            make_column_from_hint('not_numeric', pd.Series([1, 'a', 3]), {
                'stat_type': 'realAdditive'
            })

    def test_logarithmic_hint_problem(self):
        with self.assertRaises(ValueError):
            make_column_from_hint('not_numeric', pd.Series([-1, 0, 1]), {
                'stat_type': 'realMultiplicative'
            })


if __name__ == '__main__':
    unittest.main()
