import unittest
import sys
from vaquero.invocation_tools import (_clean_filename,
                                      _extract_args,
                                      _extract_invocations,
                                      _name_of,
                                      callables_from,
                                      no_filter)


def run_and_get_last_traceback(f):
    try:
        f()
    except ValueError:
        tb = sys.exc_info()[2]
        while tb.tb_next:
            tb = tb.tb_next
        return tb


def run_and_return_traceback(f):
    try:
        f()
    except ValueError:
        return sys.exc_info()[2]


class TestInvocationTools(unittest.TestCase):
    def test__clean_filename(self):
        examples = [(  # A common filename example
                     "/site-packages/IPython/core/interactiveshell.py",
                     "interactiveshell.py"),
                    (  # An Ipython example
                     "<ipython-input-111-8515003c2eb6>", "In [111]")]

        for file_name, expected in examples:
            self.assertEqual(_clean_filename(file_name), expected)

    def test__extract_args(self):
        def func_with_no_args():
            a = 100
            raise ValueError()
        tb = run_and_get_last_traceback(func_with_no_args)
        self.assertIsNone(_extract_args(tb.tb_frame), 100)

        def func_with_positional_and_kw_args(x, y, z=100):
            name = 'something'
            raise ValueError()
        invocation = lambda: func_with_positional_and_kw_args('a', 10)
        tb = run_and_get_last_traceback(invocation)
        self.assertEqual(_extract_args(tb.tb_frame), ['a', 10, 100])

    def test__extract_invocations(self):
        from tests.invocation_example import f
        # sqrt(2(3 + 5)) = 4)
        self.assertEqual(f(3, 5), 4)

        # sqrt(-4) = ValueError
        tb = run_and_return_traceback(lambda: f(3, -5))

        def is_interesting(invoc):
            return invoc['name'] in {'scale', 'square_rooted', 'f'}

        expected = [{'call_args': [3, -5],
                     'filename': 'invocation_example.py',
                     'lineno': 20,
                     'name': 'f'},
                    {'call_args': [-2],
                     'filename': 'invocation_example.py',
                     'lineno': 16,
                     'name': 'scale'},
                    {'call_args': [-4],
                     'filename': 'invocation_example.py',
                     'lineno': 7,
                     'name': 'square_rooted'}]
        invocations = _extract_invocations(tb, is_interesting)
        self.assertEqual(invocations, expected)

        self.assertTrue(no_filter({}))

    def test__callables_from(self):
        import tests.invocation_example
        callables = callables_from(tests.invocation_example)

        # I think the order could vary by implementation.
        self.assertEqual(sorted(callables),
                         sorted(['f', 'scale', 'square_rooted', 'ignore_me']))

        callables = callables_from(tests.invocation_example,
                                   include_private=True)

        # I think the order could vary by implementation.
        self.assertEqual(sorted(callables),
                         sorted(['_private_function',
                                 'f', 'scale', 'square_rooted', 'ignore_me']))

        class Klass:
            N = 100
            def b(self):
                pass
            def _private_method(self):
                pass

        self.assertEqual(callables_from(Klass), ['b'])  # Class
        self.assertEqual(callables_from(Klass()), ['b'])  # Instance

    def test__name_of(self):
        def f():
            pass

        self.assertEqual(_name_of(f), 'f')
        self.assertEqual('f', 'f')


if __name__ == '__main__':
    from tests import invocation_example
    unittest.main()
