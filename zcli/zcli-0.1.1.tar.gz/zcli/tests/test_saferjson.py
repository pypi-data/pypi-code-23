import unittest
from cStringIO import StringIO
from textwrap import dedent
from decimal import Decimal
from genty import genty, genty_dataset
from zcli.saferjson import \
    dump_compact, \
    dump_pretty, \
    dumps_compact, \
    dumps_pretty, \
    encode_param, \
    loads


@genty
class encode_param_tests (unittest.TestCase):
    @genty_dataset(
        string=('foo', 'foo'),
        true=(True, 'true'),
        false=(False, 'false'),
        integer=(42, '42'),
        decimal=(Decimal('42.03489096'), '42.03489096'),
        text=(u'bar', '"bar"'),
        array_empty=([], '[]'),
        array_full=(['a', 'b', 'c'], '["a","b","c"]'),
        object_empty=({}, '{}'),
        object_full=(
            {'a': 'apple', 'b': 'banana', 'c': 'coconut'},
            '{"a":"apple","b":"banana","c":"coconut"}',
        ),
    )
    def test_encode_arg(self, value, expected):
        actual = encode_param(value)
        self.assertEqual(actual, expected)

    @genty_dataset(
        null=(None,),
        float=(3.1415,),
    )
    def test_encode_arg_bad_value(self, value):
        self.assertRaises(AssertionError, encode_param, value)


@genty
class loads_tests (unittest.TestCase):
    @genty_dataset(
        from_int=('1',),
        from_float=('1.0',),
    )
    def test_decimal_parsing(self, input):
        expected = Decimal(input)
        actual = loads(input)
        self.assertIsInstance(actual, Decimal)
        self.assertEqual(expected, actual)

    def test_duplicate_keys_fail(self):
        self.assertRaisesRegexp(
            ValueError, r'Duplicate key "foo".',
            loads, '{"foo": 42, "foo": 42}',
        )


# A helper for thorough genty datasets:
def _genty_cartesian_product(a, b):
    prod = {}
    for (ka, ta) in a.iteritems():
        assert type(ta) is tuple, repr((ka, ta))
        for (kb, tb) in b.iteritems():
            assert type(tb) is tuple, repr((kb, tb))
            prod['{}, {}'.format(ka, kb)] = ta + tb
    return prod


@genty
class dumps_tests (unittest.TestCase):
    pretty_and_compact_args = dict(
        null=(None,),
        string=('foo',),
        decimal=(Decimal('3.1415000'),),
        empty_array=([],),
        empty_object=({},),
    )

    @genty_dataset(**pretty_and_compact_args)
    def test_pretty_and_compact(self, input):
        actualpretty = dumps_pretty(input)
        actualcompact = dumps_compact(input)
        self.assertEqual(actualpretty, actualcompact)

    pretty_versus_compact_args = dict(
        null_in_array=([None], '[null]', '[\n  null\n]'),
        null_in_object=({u'x': None}, '{"x":null}', '{\n  "x": null\n}'),
        complicated=(
            {
                u'x': [None, Decimal('3.1415000')],
                u'y': [],
                u'z': u'foo!',
            },
            '{"x":[null,3.1415],"y":[],"z":"foo!"}',
            dedent('''\
              {
                "x": [
                  null,
                  3.1415
                ],
                "y": [],
                "z": "foo!"
              }
            '''.rstrip()),
        ),
    )

    @genty_dataset(**pretty_versus_compact_args)
    def test_compact(self, input, expectedcompact, _):
        actualcompact = dumps_compact(input)
        self.assertEqual(expectedcompact, actualcompact)

    @genty_dataset(**pretty_versus_compact_args)
    def test_pretty(self, input, _, expectedpretty):
        actualpretty = dumps_pretty(input)
        self.assertEqual(expectedpretty, actualpretty)

    # Test round-trip encode/decode for all args:
    all_values_args = {}
    all_values_args.update(pretty_and_compact_args)
    all_values_args.update(
        dict(
            (k, a[:1])
            for (k, a)
            in pretty_versus_compact_args.iteritems()
        )
    )

    @genty_dataset(
        **_genty_cartesian_product(
            dict(
                compact=(dumps_compact,),
                pretty=(dumps_pretty,),
            ),
            all_values_args,
        )
    )
    def test_roundtrip_encode_decode(self, dumps, v):
        text = dumps(v)
        v2 = loads(text)
        self.assertEqual(v, v2)

    @genty_dataset(
        **_genty_cartesian_product(
            dict(
                compact=(dumps_compact, dump_compact),
                pretty=(dumps_pretty, dump_pretty),
            ),
            dict(
                pretty_and_compact_args.items() +
                pretty_versus_compact_args.items()
            )
        )
    )
    def test_dump_vs_dumps_equiv(self, dumps, dump, value, *_extraignored):
        actuals = dumps(value)
        f = StringIO()
        dump(value, f)
        actualf = f.getvalue()
        self.assertEqual(actuals, actualf)

    def test_dumps_float_precision_error(self):
        d = Decimal('3e30')
        self.assertRaisesRegexp(
            ValueError, r'^Encoding decimal.*introduces error: ',
            dumps_compact, d,
        )

    def test_dumps_float_precision_error_okay_because_too_small(self):
        d = Decimal(0.1 + 0.2)
        text = dumps_compact(d)
        d2 = loads(text)
        error = abs(d-d2)
        self.assertLess(error, Decimal('0.000000001'))
