#! /usr/bin/env python

import unittest
from decimal import Decimal
from dimana import _units
from dimana._units import \
    Scalar, \
    Units, \
    UnitsMismatch, \
    UnitsParseError
from dimana._value import Value
from dimana.tests.util import ParseTestClass


class UnitsUniquenessTests (unittest.TestCase):
    def test_value_type_construction(self):
        u1 = Units({})
        u2 = Units({})
        self.assertIs(u1, u2)

        u1 = Units({'meter': 1})
        u2 = Units({'meter': 1})
        self.assertIs(u1, u2)

        u1 = Units({'meter': 1, 'sec': -2})
        u2 = Units({'meter': 1, 'sec': -2})
        self.assertIs(u1, u2)

    def test_scalar(self):
        self.assertIs(Scalar, Units({}))


class UnitsValueConstructorTests (unittest.TestCase):
    def test_zero_and_one(self):
        unitses = [
            Scalar,
            Units('GROM'),
        ]

        for u in unitses:
            self.assertIsInstance(u.zero, Value)
            self.assertIsInstance(u.one, Value)
            self.assertEqual(Decimal('0'), u.zero.amount)
            self.assertEqual(Decimal('1'), u.one.amount)
            self.assertEqual(Scalar.one, u.one / u.one)
            self.assertEqual(u.zero, u.one * Scalar.zero)
            self.assertIs(u**2, (u.zero * u.one).units)

    def test_maker(self):
        inputs = [
            '0',
            '1',
            '1.00',
            '+17e3',
            '-42.07000',
            0,
            1,
            42.3,
        ]

        unitses = [
            Scalar,
            Units('GROM'),
        ]

        for units in unitses:
            for i in inputs:
                self.assertEqual(
                    units(i),
                    Value(Decimal(i), units),
                )


class UnitsArithmeticOperationsTests (unittest.TestCase):
    def setUp(self):
        self.m = Units({'meter': 1})
        self.s = Units({'sec': 1})

        # All equivalences are tested for each case here:
        self.eqcases = [Scalar, self.m, self.m * self.s, self.m / self.s]

    def test__add__(self):
        self.assertIs(self.m, self.m + self.m)

    def test__add__UnitsMismatch(self):
        self.assertRaises(UnitsMismatch, lambda: self.m + self.s)

    def test__add__TypeError(self):
        self.assertRaises(TypeError, lambda: self.m + 'banana')

    def test__inv__(self):
        self.assertIs(self.m, -self.m)

    def test__mul__(self):
        self.assertIs(
            Units({'meter': 1, 'sec': 1}),
            self.m * self.s,
        )

    def test__mul__TypeError(self):
        self.assertRaises(TypeError, self.m.__mul__, 42)

    def test__div__(self):
        self.assertIs(
            Units({'meter': 1, 'sec': -1}),
            self.m / self.s,
        )

    def test__div__TypeError(self):
        self.assertRaises(TypeError, self.m.__div__, 42)

    def test__pow__(self):
        self.assertIs(
            Units({'meter': 3}),
            self.m ** 3,
        )

    def test__sub__is__add__(self):
        self.assertEqual(Units.__sub__, Units.__add__)

    def test__truediv__is__div__(self):
        self.assertEqual(Units.__truediv__, Units.__div__)

    # Equivalences:
    def test_scalar_cancellation_equivalence(self):
        for u in self.eqcases:
            self.assertIs(Scalar, u / u)

    def test_scalar_0_power(self):
        for u in self.eqcases:
            self.assertIs(Scalar, u ** 0)

    def test_mul_pow_equivalence(self):
        for u in self.eqcases:
            self.assertIs(u * u, u ** 2)

    def test_div_inverse_mul_equivalence(self):
        for u in self.eqcases:
            for k in self.eqcases:
                self.assertIs(u / k, u * (k ** -1))


@ParseTestClass(Units, Units, UnitsParseError)
class UnitsParseAndStrTests (unittest.TestCase):

    def assertParsedValueMatches(self, a, b):
        self.assertIs(a, b)

    m = Units({'meter': 1})
    s = Units({'sec': 1})
    kg = Units({'kg': 1})

    cases = [
        (Scalar,
         '1',
         ['foo^0',
          'x/x']),

        (s**(-2),
         '1 / sec^2',
         ['1/sec^2',
          'sec^-2',
          '1/(sec*sec)',
          '1/ ( sec  * sec )']),

        (m,
         'meter',
         []),

        (s,
         'sec',
         []),

        (m*s,
         'meter * sec',
         ['meter*sec',
          '1/(meter^-1*sec^-1)']),

        (m/s,
         'meter / sec',
         ['sec*meter / sec^2']),

        (m**2 * s,
         'meter^2 * sec',
         ['meter*sec*meter']),

        (m / s**2,
         'meter / sec^2',
         []),

        (m**2 / s**2,
         'meter^2 / sec^2',
         []),

        (kg**2 * m / s**2,
         'kg^2 * meter / sec^2',
         []),

        (s**2 / (kg*m),
         'sec^2 / (kg * meter)',
         []),

        (s**1.5,
         'sec^1.5',
         []),
    ]

    errorcases = [
        # These should trigger the top-level regex mismatch:
        '',
        '%',  # Doesn't match character classes.
        '1foo',  # Doesn't match initial character class.
        ' meter',  # No initial whitespace.
        'meter ',  # No trailing whitespace.

        # This should trigger error on unpacking of term parts:
        'a^b^c',

        # This should trigger error on int parsing of power:
        'a^b',

        # This should trigger error on unit name parsing of term:
        'a ^2',
    ]


class UnitsDeprecatedAPITests (unittest.TestCase):
    def test_Mismatch(self):
        self.assertFalse(hasattr(Units, 'Mismatch'))

    def test_ParseError(self):
        self.assertFalse(hasattr(Units, 'ParseError'))

    def test_no_parse(self):
        self.assertFalse(hasattr(Units, 'parse'))

    def test_no_mod_parse(self):
        self.assertFalse(hasattr(_units, 'parse_units'))

    def test_no_scalar(self):
        self.assertFalse(hasattr(Units, 'scalar'))
