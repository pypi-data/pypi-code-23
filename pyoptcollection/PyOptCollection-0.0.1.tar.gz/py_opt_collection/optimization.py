"""Docstring for Optimization module."""

import time
import inspect
import statistics
from copy import copy
from random import Random, randint


class Optimization(object):
    """Optimization class is where the problem put in. In here we define the
    mathematical model together with other constraints, variables' types, or
    how will the program will generate random numbers by defining the seed."""

    def __init__(self,
                 optimizing_function,
                 boundaries,
                 **kwargs):
        """

        :param optimizing_function: A function which received a tuple of number
        and return a final calculated value.
        :type optimizing_function: (tuple[number]) -> number
        :param boundaries: list of tuples contains upper and lower limit of
        variables.
        :type boundaries: list[tuple[number]]
        :param no_dimensions: Number of total variable in the problem.
        :type no_dimensions: int
        :param find_max: Is this optimization used to find Max
        (if not then it is Min).
        :type find_max: bool
        :param seed: used as an predefined method to control how example data
        being generated.
        :type seed: int
        """

        self.func = optimizing_function
        self.boundaries = boundaries
        self.no_dimensions = kwargs.get('no_dimensions', 1)
        self.find_max = kwargs.get('find_max', False)

        self.random_generator = Random()
        seed = kwargs.get('seed', None)
        self.random_generator.seed(int(time.time()) if seed is None else seed)

        self.constraints = list()

    def add_constraint(self, constraint_func):
        """

        :param constraint_func:
        :type constraint_func: optimizing_function: (tuple[number]) -> bool
        """

        self.constraints.append(constraint_func)

    def check_constraints(self, position):
        """Check if one position satisfy all the constraints of the
        optimization including individual variable's boundaries."""
        ret = True
        for dim in range(self.no_dimensions):
            ret &= self.boundaries[dim][0] <= \
                   position[dim] <= \
                   self.boundaries[dim][1]
        for func in self.constraints:
            ret &= func(position)
        return ret

    def __repr__(self):
        return "Optimization Object\n" \
               "===================\n" \
               "  Optimization Function: \n  " + \
               "  ".join(inspect.getsourcelines(self.func)[0]) + \
               "  ------------------\n" + \
               "  Variables: " + \
               "  ".join(["x%d" % i for i in range(self.no_dimensions)]) + \
               "\n" + \
               "  ------------------\n" + \
               "  Boundaries: \n  " + \
               "  ".join(
                   ["x%d: %s\n" % (i, self.boundaries[i])
                    for i in range(self.no_dimensions)]
               ) + "\n" + \
               "  ------------------\n" + \
               "  Constraints: \n    " + \
               "    ".join([
                   "    ".join(
                       inspect.getsourcelines(f)[0]
                   ) for f in self.constraints
               ]) + "\n==================="


class OptimizationMixin(object):
    """This Mixin allow classes a faster way to access Optimization object's
    attributes."""

    optimization_object = None

    @property
    def find_max(self):
        """Shortening the way to access Optimization.find_max attribute."""
        return self.optimization_object.find_max

    @property
    def no_dimensions(self):
        """Shortening the way to access Optimization.no_dimensions
        attribute."""
        return self.optimization_object.no_dimensions

    @property
    def boundaries(self):
        """Shortening the way to access Optimization.boundaries attribute."""
        return self.optimization_object.boundaries

    @property
    def random_generator(self):
        """Shortening the way to access Optimization.random_generator
        attribute."""
        return self.optimization_object.random_generator


class AlgorithmObject(OptimizationMixin):
    """This is the skeleton for other algorithm objects, for example: PSO.
    The skeleton has some class' functions and properties to be used."""

    def __init__(self, optimization_object, **kwargs):
        """
        In this constructor function defined basic attributes for the classes.

        :param optimization_object: Initialized Optimization object. By passing
        it into AlgorithmObject classes, we can pass information easily between
        instances with many layer of classes.
        :type optimization_object: Optimization
        :param verbose: Will the AlgorithmObject(s) print out log during
        its/their runtime.
        :type verbose: bool
        :param historical: Telling the object(s) to store historical snapshots
        or not.
        :type historical: bool
        :param is_copy: This object is copy from other Algorithm object,
        therefore need to update the seed. Default False.
        :type is_copy: bool
        """

        self.optimization_object = optimization_object
        self.best = (None, None)

        self.verbose = kwargs.get('verbose', False)

        if kwargs.get('historical', False):
            self.snapshots = list()

        if kwargs.get('is_copy', False):
            timestamp = int(time.time())
            self.optimization_object.random_generator.\
                seed(timestamp + randint(1, timestamp))

    def solve(self):
        """
        Do solving and return the best result of the optimization.

        :return: Optimized position and value.
        :rtype: (number, list[number])
        """

        self.best = (self.random_generator.random(),
                     [self.random_generator.random()])
        return self.best

    def __copy__(self):
        kwargs = copy(self.__dict__)
        kwargs['is_copy'] = True
        return type(self)(**kwargs)


class MultipleSolving(object):
    """Use this class whenever you want to run one optimization more than one
    times."""

    def __init__(self, algorithm_obj, no_tries):
        """
        Constructor for MultipleSolving class.

        :param algorithm_obj: Initialized AlgorithmObject's classes' object.
        :type algorithm_obj: AlgorithmObject
        :param no_tries: Number of trials the whenever MultipleSolving.run()
        is executed.
        :type no_tries: int
        """

        self.ori_algorithm_obj = algorithm_obj
        self.no_tries = no_tries
        self.results = list()
        self.totals_time = list()
        self.results_value_only = list()
        self.stat = dict()
        self.is_run = False

    def _exec_algorithm_object(self, algorithm_obj):
        _t = time.process_time()
        self.results.append(algorithm_obj.solve())
        self.totals_time.append(time.process_time() - _t)

    def run(self, pool=None):
        """
        Start running the optimizations, then sort the results.

        :param pool: multiprocessing.Pool object, used for parallel computing.
        :return: None
        """
        algorithm_objects = list()
        for _i in range(self.no_tries):
            algorithm_objects.append(copy(self.ori_algorithm_obj))
        if pool:
            pool.map(self._exec_algorithm_object, algorithm_objects)
            pool.close()
            pool.join()
        else:
            for algorithm_object in algorithm_objects:
                self._exec_algorithm_object(algorithm_object)

        self.results = sorted(self.results,
                              reverse=self.ori_algorithm_obj.find_max)
        self.results_value_only = [x[0] for x in self.results]
        self.stat['mean'] = statistics.mean(self.results_value_only)
        self.stat['median'] = statistics.median(self.results_value_only)
        self.stat['variance'] = \
            statistics.variance(self.results_value_only)
        self.stat['range'] = abs(
            self.results_value_only[0] - self.results_value_only[-1]
        )
        self.stat['average_runtime'] = statistics.mean(self.totals_time)
        self.is_run = True

    @property
    def best_result(self):
        """Return the best result of multiple ran, this required
        MultipleSolving.run() function have to be run first."""
        if self.is_run:
            return self.results[0]
        else:
            raise AttributeError(
                'MultipleSolving.run() must be run first in order to fetch '
                'best result.')

    def __repr__(self):
        ret_str = "Multiple solving for: %s" % self.ori_algorithm_obj + \
                  ",\n    number of tries: %d." % self.no_tries
        if self.is_run:
            ret_str += "\nBest result: %s " \
                       "with coordination at %s" % self.best_result
            ret_str += "\nStats:\n    Range (best value - worse value): " \
                       "\n        {range}s" \
                       "\n    Mean: \n        {mean}" \
                       "\n    Median: \n        {median}" \
                       "\n    Variance: \n        {variance}".\
                format(**self.stat)

        return ret_str
