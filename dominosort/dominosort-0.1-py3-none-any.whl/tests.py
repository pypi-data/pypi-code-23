from functools import partial
from random import random, shuffle
import unittest

from dominosort.metrics import ManhattanDistance, EuclideanDistance
from dominosort.solver import Solver, BranchAndBound


def add_test_sizes(method_name):
    def decorator(cls):
        def _generate_test_method(_size):
            def test(self):
                getattr(self, method_name)(_size)
            return test

        fmt_string = '{}_{:0%dd}' % len(str(max(cls.sizes)))
        for size in cls.sizes:
            setattr(
                cls,
                fmt_string.format(method_name.lstrip('_'), size),
                _generate_test_method(size)
            )
        return cls
    return decorator


class TestSolver(unittest.TestCase):
    solver = Solver
    sizes = range(5, 31, 5)

    @classmethod
    def setUpClass(cls):
        cls.solver.sort = partial(cls.solver.sort, maxiter=1000000)

    @staticmethod
    def _generate_optimal_sequential_solution_using_scalars(count):
        return [(float(i)/count, float(i+1)/count) for i in range(count)]

    @staticmethod
    def _generate_optimal_random_solution_using_scalars(count):
        items = [(random(), random())]
        for _ in range(count - 1):
            items.append((items[-1][1], random()))
        return items

    def _test_reversed_sequential(self, size, metric):
        items = self._generate_optimal_sequential_solution_using_scalars(size)
        self.assertSequenceEqual(
            self.solver.sort(list(reversed(items)), metric),
            items
        )

    def _test_shuffle_sequential(self, size, metric):
        items = self._generate_optimal_sequential_solution_using_scalars(size)
        test_items = [x for x in items]
        shuffle(test_items)
        self.assertSequenceEqual(
            self.solver.sort(test_items, metric),
            items
        )

    def _test_reversed_random(self, size, metric):
        items = self._generate_optimal_random_solution_using_scalars(size)
        # Multiple solutions may be possible, so we need to compare the loss.
        # In fact the solutions are constructed to have zero loss however
        # due to numerical accuracy it's better to actually compute it.
        self.assertEqual(
            self.solver.loss(self.solver.sort(list(reversed(items)), metric), metric),
            self.solver.loss(items, metric)
        )

    def _test_shuffle_random(self, size, metric):
        items = self._generate_optimal_random_solution_using_scalars(size)
        test_items = [x for x in items]
        shuffle(test_items)
        # Multiple solutions may be possible, so we need to compare the loss.
        # In fact the solutions are constructed to have zero loss however
        # due to numerical accuracy it's better to actually compute it.
        self.assertEqual(
            self.solver.loss(self.solver.sort(test_items, metric), metric),
            self.solver.loss(items, metric)
        )

    def _test_manhattan_scalar_reversed_sequential(self, size):
        self._test_reversed_sequential(size, ManhattanDistance)

    def _test_manhattan_scalar_shuffle_sequential(self, size):
        self._test_shuffle_sequential(size, ManhattanDistance)

    def _test_manhattan_scalar_reversed_random(self, size):
        self._test_reversed_random(size, ManhattanDistance)

    def _test_manhattan_scalar_shuffle_random(self, size):
        self._test_shuffle_random(size, ManhattanDistance)

    def _test_euclidean_scalar_reversed_sequential(self, size):
        self._test_reversed_sequential(size, EuclideanDistance)

    def _test_euclidean_scalar_shuffle_sequential(self, size):
        self._test_shuffle_sequential(size, EuclideanDistance)

    def _test_euclidean_scalar_reversed_random(self, size):
        self._test_reversed_random(size, EuclideanDistance)

    def _test_euclidean_scalar_shuffle_random(self, size):
        self._test_shuffle_random(size, EuclideanDistance)


@add_test_sizes('_test_manhattan_scalar_reversed_sequential')
@add_test_sizes('_test_manhattan_scalar_shuffle_sequential')
@add_test_sizes('_test_manhattan_scalar_reversed_random')
@add_test_sizes('_test_manhattan_scalar_shuffle_random')
@add_test_sizes('_test_euclidean_scalar_reversed_sequential')
@add_test_sizes('_test_euclidean_scalar_shuffle_sequential')
@add_test_sizes('_test_euclidean_scalar_reversed_random')
@add_test_sizes('_test_euclidean_scalar_shuffle_random')
class TestBranchAndBound(TestSolver):
    solver = BranchAndBound
    sizes = range(5, 31, 5)


del TestSolver


if __name__ == '__main__':
    unittest.main()
