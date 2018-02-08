import unittest
from vaquero.pipeline import *
import os

#THIS_DIR = os.path.dirname(os.path.realpath(__file__))
#INVOCATION_EXAMPLE_PATH = os.path.join("invocation_example.py")
#PIPELINE_EXAMPLE_PATH = os.path.join("pipeline_example.py")
from tests import invocation_example, pipeline_example


class TestPipeline(unittest.TestCase):

    def test_collect_func_ordering(self):

        fs = collect_func_ordering(invocation_example)
        expected = ['square_rooted', 'ignore_me', 'scale',
                    'f', '_private_function']
        self.assertEqual(fs, expected)
        self.assertEqual(fs,
                         collect_func_ordering(invocation_example.__file__))

    def test_collect_pipeline(self):
        fs = collect_pipeline(invocation_example, skip_private=False)
        expected = ['square_rooted', 'ignore_me', 'scale',
                    'f', '_private_function']
        names = [f.__name__ for f in fs]
        self.assertEqual(names, expected)

        fs = collect_pipeline(invocation_example, reloading=False)
        expected = ['square_rooted', 'ignore_me', 'scale', 'f']
        names = [f.__name__ for f in fs]
        self.assertEqual(names, expected)


class TestPipeline(unittest.TestCase):
    def test_done_sentinel(self):
        import math
        results = []

        def f(x):
            if x < 0:
                results.append("err")
                return Done

        def g(x):
            results.append(math.sqrt(x))

        pipeline = Pipeline()
        pipeline._pipeline.extend([f, g])

        pipeline(-4)
        pipeline(4)
        self.assertEqual(results, ['err', 2])

    def test_skip_to(self):
        import math
        results = []

        def f(x):
            if x < 0:
                return SkipTo(h)

        def g(x):
            results.append(math.sqrt(x))

        def h(x):
            results.append(x * 2)

        pipeline = Pipeline()
        pipeline._pipeline.extend([f, g, h])

        pipeline(-4)
        pipeline(4)
        self.assertEqual(results, [-8, 2.0, 8])


class TestModulePipeline(unittest.TestCase):
    def test_init(self):
        pipeline = ModulePipeline(invocation_example,
                                  skip_private_applications=True,
                                  include_private_captures=True,
                                  reloading=True)

        self.assertEqual([f.__name__ for f in pipeline._pipeline],
                         ['square_rooted', 'ignore_me', 'scale', 'f'])
        self.assertEqual([f.__name__ for f in pipeline],
                         ['square_rooted', 'ignore_me', 'scale',
                          'f', '_private_function'])

        pipeline = ModulePipeline(invocation_example,
                                  skip_private_applications=False,
                                  include_private_captures=False,
                                  reloading=True)
        self.assertEqual([f.__name__ for f in pipeline._pipeline],
                         ['square_rooted', 'ignore_me', 'scale',
                          'f', '_private_function'])
        self.assertEqual([f.__name__ for f in pipeline],
                         ['square_rooted', 'ignore_me', 'scale', 'f'])

    def test_call(self):
        pipeline = ModulePipeline(pipeline_example)
        items = []
        pipeline(items)
        self.assertEqual(items, [200]*10)

