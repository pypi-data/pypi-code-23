import unittest
from vaquero import Vaquero, VaqueroException, callables_from
import tests.invocation_example


class TestVaquero(unittest.TestCase):
    def test_vaquero(self):  # Integration test, mostly.
        from tests.invocation_example import f, square_rooted
        vaquero = Vaquero(2)
        vaquero.register_targets(callables_from(tests.invocation_example))
        self.assertEqual(vaquero.target_funcs,
                         set(['ignore_me', 'scale', 'f', 'square_rooted']))

        # Doesn't raise an exception.
        doc = {'x': 10, 'y': 20}
        with vaquero.on_input(doc):
            f(doc['x'], doc['y'])
        self.assertEqual(vaquero.stats(),
                         {'failures': 0, 'ignored': 0,
                          'failures_by': {}, 'successes': 1})
        self.assertEqual(vaquero.last_input, doc)
        self.assertTrue(vaquero.was_successful)

        # Raise an exception.
        doc = {'x': 10, 'y': -20}
        with vaquero.on_input(doc):
            f(doc['x'], doc['y'])
        self.assertEqual(vaquero.stats(),
                         {'failures': 1, 'ignored': 0,
                          'failures_by': {'square_rooted': 1},
                          'successes': 1})
        self.assertEqual(vaquero.n_failures, 1)
        self.assertEqual(vaquero.stats_ignoring(ValueError),
                         {'failures': 0, 'ignored': 1,
                          'failures_by': {},
                          'successes': 1})
        self.assertEqual(vaquero.stats_ignoring('FakeValue'),
                         {'failures': 1, 'ignored': 0,
                          'failures_by': {'square_rooted': 1},
                          'successes': 1})
        self.assertEqual(vaquero.last_input, doc)
        self.assertFalse(vaquero.was_successful)

        # Raise another exception but on an unregistered function.
        def unregistered():
            raise ValueError("Some bad value")

        # Raise another, but one too many!
        with self.assertRaises(ValueError):
            with vaquero:
                unregistered()
        self.assertEqual(vaquero.stats(),
                         {'failures': 2, 'ignored': 0,
                          'failures_by': {'square_rooted': 1},
                          'successes': 1})

        # Raise another, but one too many!
        with self.assertRaisesRegexp(VaqueroException, "limit exceeded"):
            doc = {'x': 10, 'y': -30}
            with vaquero.on_input(doc):
                f(doc['x'], doc['y'])

        self.assertEqual(vaquero.stats(),
                         {'failures': 3, 'ignored': 0,
                          'failures_by': {'square_rooted': 2},
                          'successes': 1})
        self.assertEqual(vaquero.last_input, doc)

        # Examine captures on unregistered function.
        self.assertEqual(vaquero.examine("not_present"), [])

        expected = [{'call_args': [-20],
                     'filename': 'invocation_example.py',
                     'exc_type': 'ValueError',
                     'exc_value': 'math domain error',
                     'lineno': 7,
                     'name': 'square_rooted'},
                    {'call_args': [-40],
                     'filename': 'invocation_example.py',
                     'exc_type': 'ValueError',
                     'exc_value': 'math domain error',
                     'lineno': 7,
                     'name': 'square_rooted'}]
        self.assertEqual(vaquero.examine(square_rooted), expected)

        self.assertEqual(vaquero.examine(square_rooted, "[*].filename", True),
                         set(['invocation_example.py']))

    def test_vaquero_stops_on_keyboard_interrupt(self):
        def g():
            raise KeyboardInterrupt

        vaquero = Vaquero()
        with vaquero:
            g()

        self.assertEqual(vaquero.stats(),
                         {'ignored': 0, 'failures': 0,
                          'failures_by': {}, 'successes': 0})

    def test_no_capture(self):
        from tests.invocation_example import f
        vaquero = Vaquero(capture_error_invocations=False)
        vaquero.register_target('f')

        doc = {'x': 10, 'y': -30}
        with vaquero.on_input(doc):
            f(doc['x'], doc['y'])

        self.assertFalse(vaquero.was_successful)
        self.assertEqual(vaquero.stats()['failures_by'], {})

        # Reset-based
        vaquero = Vaquero()
        vaquero.reset(turn_off_error_capturing=True)
        vaquero.register_target('f')

        doc = {'x': 10, 'y': -30}
        with vaquero.on_input(doc):
            f(doc['x'], doc['y'])

        self.assertFalse(vaquero.was_successful)
        self.assertEqual(vaquero.stats()['failures_by'], {})

    def test_input_capturing(self):
        from tests.invocation_example import f, square_rooted
        vaquero = Vaquero(2, annotate_failure_with_input=True)
        vaquero.register_targets(callables_from(tests.invocation_example))

        # Raise an exception.
        doc = {'x': 10, 'y': -20}
        with vaquero.on_input(doc):
            f(doc['x'], doc['y'])
        self.assertEqual(vaquero.examine('square_rooted')[0],
                         {'call_args': [-20],
                          'exc_type': 'ValueError',
                          'exc_value': 'math domain error',
                          'filename': 'invocation_example.py',
                          'lineno': 7,
                          'name': 'square_rooted',
                          'top_input': doc})

    def test_execute_on_failure(self):
        from tests.invocation_example import f, square_rooted
        vaquero = Vaquero(2, annotate_failure_with_input=True)
        vaquero.register_targets(callables_from(tests.invocation_example))

        doc = {'x': 10, 'y': -25}
        with vaquero.on_input(doc):
            f(doc['x'], doc['y'])

        doc = {'x': 20, 'y': -30}
        with vaquero.on_input(doc):
            f(doc['x'], doc['y'])

        inputs = []
        capture_inputs = lambda x: inputs.append(x)
        vaquero.execute_on_failure(capture_inputs, 1, 'square_rooted')
        self.assertEqual(inputs, [-20])  # sqrt((20 - 30)*2)

        # Rewrite square rooted as you may while testing...
        def square_rooted(x):
            inputs.append(x)
        vaquero.execute_on_failure(square_rooted, 0)
        self.assertEqual(inputs, [-20, -30])  # sqrt((10 - 25)*2)

        def non_issued():
            pass

        with self.assertRaisesRegexp(VaqueroException, "has no issues"):
            vaquero.execute_on_failure(non_issued, 0)


    def test_execute_over_failure(self):
        from tests.invocation_example import f, square_rooted
        vaquero = Vaquero(2, annotate_failure_with_input=True)
        vaquero.register_targets(callables_from(tests.invocation_example))

        doc = {'x': 10, 'y': -25}
        with vaquero.on_input(doc):
            f(doc['x'], doc['y'])

        doc = {'x': 20, 'y': -30}
        with vaquero.on_input(doc):
            f(doc['x'], doc['y'])

        items = []
        collect_safely = lambda x: items.append(abs(x))
        res = vaquero.execute_over_failures(collect_safely, 'square_rooted')
        self.assertEqual(res.stats(), {'failures': 0, 'ignored': 0,
                                       'failures_by': {}, 'successes': 2})
        self.assertEqual(items, [30, 20])

        # Redefine
        items = []
        def square_rooted(x):
            items.append(abs(x))
        res = vaquero.execute_over_failures(square_rooted)
        self.assertEqual(res.stats(), {'failures': 0, 'ignored': 0,
                                       'failures_by': {}, 'successes': 2})
        self.assertEqual(items, [30, 20])

        def non_issued():
            pass

        with self.assertRaisesRegexp(VaqueroException, "has no issues"):
            vaquero.execute_over_failures(non_issued, 0)

    def test_merge(self):
        from tests.invocation_example import f, square_rooted
        a, b = Vaquero(), Vaquero()
        def fails_intentionally():
            assert False
        a.register_targets(callables_from(tests.invocation_example))
        b.register_targets(callables_from(tests.invocation_example))
        b.register_target(fails_intentionally)

        doc = {'x': 10, 'y': -20}
        with a.on_input(doc):
            f(doc['x'], doc['y'])
        self.assertEqual(a.stats(),
                         {'failures': 1, 'ignored': 0,
                          'failures_by': {'square_rooted': 1},
                          'successes': 0})

        with b:
            f(doc['x'], doc['y'])

        with b:
            fails_intentionally()
        self.assertEqual(b.stats(),
                         {'failures': 2, 'ignored': 0,
                          'failures_by': {'square_rooted': 1,
                                          'fails_intentionally': 1},
                          'successes': 0})

        a.merge(b)
        self.assertEqual(a.stats(),
                         {'failures': 3, 'ignored': 0,
                          'failures_by': {'square_rooted': 2,
                                          'fails_intentionally': 1},
                          'successes': 0})
