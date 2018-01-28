"""Test py_opt_collection.optimization 's classes."""

import pytest
from multiprocessing.dummy import Pool
from copy import copy
from py_opt_collection.optimization import Optimization, \
    OptimizationMixin, AlgorithmObject, MultipleSolving


class TestOptimization(object):
    """Tests for py_opt_collection.optimization.Optimization class."""

    def test___init__(self, fix_optimization_object_kwargs):
        """Test __init__() constructor function."""

        opt_object = Optimization(**fix_optimization_object_kwargs)
        assert opt_object.func == \
            fix_optimization_object_kwargs['optimizing_function']
        assert opt_object.no_dimensions == \
            fix_optimization_object_kwargs['no_dimensions']
        assert opt_object.boundaries == \
            fix_optimization_object_kwargs['boundaries']
        assert opt_object.find_max == \
            fix_optimization_object_kwargs['find_max']

    def test_random_generator(self, fix_optimization_object_kwargs,
                              fix_optimization_object_kwargs_with_seed):
        """Test if random_generator works, and if given it a seed, ensure
        random_generator return the same randomize numbers for each
        constructed object."""

        opt_object = Optimization(**fix_optimization_object_kwargs)
        is_different = False
        for i in range(100):
            rand_val_1 = opt_object.random_generator.random()
            rand_val_2 = opt_object.random_generator.random()
            is_different |= rand_val_1 != rand_val_2
        assert is_different

        opt_object_custom_seed_1 = \
            Optimization(**fix_optimization_object_kwargs_with_seed)
        rand_val_3 = opt_object_custom_seed_1.random_generator.random()
        rand_val_4 = opt_object_custom_seed_1.random_generator.random()

        opt_object_custom_seed_2 = \
            Optimization(**fix_optimization_object_kwargs_with_seed)
        rand_val_5 = opt_object_custom_seed_2.random_generator.random()
        rand_val_6 = opt_object_custom_seed_2.random_generator.random()

        assert rand_val_3 == rand_val_5 and rand_val_4 == rand_val_6

    def test_add_constraints(self,
                             fix_optimization_object_kwargs,
                             fix_optimization_constraint_1,
                             fix_optimization_constraint_2):
        """Test if add_constraint() work."""

        opt_object = Optimization(**fix_optimization_object_kwargs)
        opt_object.add_constraint(fix_optimization_constraint_1)
        assert opt_object.constraints.__len__() == 1
        opt_object.add_constraint(fix_optimization_constraint_2)
        assert opt_object.constraints.__len__() == 2

    def test_check_constraints(self,
                               fix_optimization_object_kwargs,
                               fix_optimization_constraint_1,
                               fix_optimization_constraint_2):
        """
        Test check constraints function work.

        Success cases:
        - Boundaries check work
        - Constraints check work
        """

        opt_object = Optimization(**fix_optimization_object_kwargs)
        opt_object.add_constraint(fix_optimization_constraint_1)
        opt_object.add_constraint(fix_optimization_constraint_2)

        # Boundaries fail check
        assert not opt_object.check_constraints([-4])

        # Constraint 1 fail check
        assert not opt_object.check_constraints([-1.6])

        # Constraint 2 fail check
        assert not opt_object.check_constraints([0.0])

        # Satisfy all check
        assert opt_object.check_constraints([-1.8])
        assert opt_object.check_constraints([0.9])

    def test___repr__(self,
                      fix_optimization_object_kwargs,
                      fix_optimization_constraint_1):
        """Test __repr__ function."""

        opt_object = Optimization(**fix_optimization_object_kwargs)
        opt_object.add_constraint(fix_optimization_constraint_1)
        print_string = opt_object.__repr__()
        print_string.find("x[0] ** 4 + x[0] ** 3 - 3 * (x[0] ** 2) + 1")
        print_string.find("x0: (-3, 3)")
        print_string.find("x[0]**4 + x[0]**3 - 2*(x[0] ** 2) + 2 >= 0")


class TestOptimizationMixin(object):
    """Test for py_opt_collection.optimization.OptimizationMixin class."""

    @staticmethod
    def test_mixin():
        var_no_dimensions = 2
        var_boundaries = [(1, 2), (4, 5)]
        var_find_max = False
        var_random_generator = object()

        class OptObject(object):
            def __init__(self):
                self.no_dimensions = var_no_dimensions
                self.boundaries = var_boundaries
                self.find_max = var_find_max
                self.random_generator = var_random_generator

        class CClass(OptimizationMixin):
            def __init__(self, opt_object):
                self.optimization_object = opt_object

        optimization_object = OptObject()
        cc_object = CClass(optimization_object)

        assert cc_object.no_dimensions == var_no_dimensions
        assert cc_object.boundaries == var_boundaries
        assert cc_object.find_max == var_find_max
        assert cc_object.random_generator == var_random_generator


class TestAlgorithmObject(object):
    """Test for py_opt_collection.optimization.AlgorithmObject class."""

    def test___init__(self, fix_optimization_object):
        """Test __init__() constructor function."""

        algorithm_obj_1 = AlgorithmObject(
            optimization_object=fix_optimization_object
        )
        assert algorithm_obj_1.optimization_object == fix_optimization_object
        assert not algorithm_obj_1.verbose
        with pytest.raises(AttributeError):
            print(algorithm_obj_1.snapshots)

        algorithm_obj_2 = AlgorithmObject(
            optimization_object=fix_optimization_object,
            verbose=True,
            historical=True
        )
        assert algorithm_obj_2.optimization_object == fix_optimization_object
        assert algorithm_obj_2.verbose
        assert isinstance(algorithm_obj_2.snapshots, list)

        algorithm_obj_3 = copy(algorithm_obj_2)
        rand_val_2_1 = algorithm_obj_2.random_generator.random()
        rand_val_2_2 = algorithm_obj_2.random_generator.random()
        rand_val_3_1 = algorithm_obj_3.random_generator.random()
        rand_val_3_2 = algorithm_obj_3.random_generator.random()
        assert rand_val_2_1 != rand_val_3_1
        assert rand_val_2_2 != rand_val_3_2

    def test_solve(self, fix_optimization_object):
        algorithm_obj = AlgorithmObject(fix_optimization_object)
        result = algorithm_obj.solve()
        assert isinstance(result, tuple)
        assert isinstance(result[0], float)
        assert isinstance(result[1], list)


class TestMultipleSolving(object):
    """Test for py_opt_collection.optimization.MultipleSolving class."""

    def test___init__(self, fix_algorithm_object):
        """Test __init__() constructor function."""

        ms = MultipleSolving(fix_algorithm_object, 20)
        assert ms.ori_algorithm_obj == fix_algorithm_object
        assert ms.no_tries == 20
        assert isinstance(ms.results, list)
        assert isinstance(ms.results_value_only, list)
        assert isinstance(ms.stat, dict)
        assert not ms.is_run

    def test_run(self, fix_algorithm_object):
        ms = MultipleSolving(fix_algorithm_object, 20)
        ms.run()
        assert ms.is_run
        assert not (
                fix_algorithm_object.find_max !=
                (ms.results_value_only[0] > ms.results_value_only[-1])
        )

    def test_run_with_pool(self, fix_algorithm_object):
        ms = MultipleSolving(fix_algorithm_object, 20)
        pool = Pool(2)
        ms.run(pool=pool)
        assert ms.is_run
        assert not (
                fix_algorithm_object.find_max !=
                (ms.results_value_only[0] > ms.results_value_only[-1])
        )

    def test_best_result(self, fix_algorithm_object):
        ms = MultipleSolving(fix_algorithm_object, 20)
        with pytest.raises(AttributeError):
            print(ms.best_result)
        ms.run()
        assert isinstance(ms.best_result, tuple)
        assert isinstance(ms.best_result[0], float)
        assert isinstance(ms.best_result[1], list)

    def test___repr__(self, fix_algorithm_object):
        ms = MultipleSolving(fix_algorithm_object, 20)
        assert ms.__repr__().find("Multiple") != -1
        ms.run()
        print_string = ms.__repr__()
        for s in [
            "Multiple solving for",
            "Best result",
            "Stat",
            "Range",
            "Mean",
            "Median"
        ]:
            assert print_string.find(s) != -1
