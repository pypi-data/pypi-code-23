"""
This module contains simplex search algorithms.
"""

import numpy as np

from optproblems.base import ResourcesExhausted, Individual, Stalled, Aborted
from optproblems.base import Problem, BoundConstraintsRepair, ScalingPreprocessor

from dfoalgos.base import Observable, OptimizeResult, scale, displace, center_of_mass
from dfoalgos.base import lexicographic_sort_key, create_tilted_regular_simplex


class SimplexSearch(Observable):
    """Abstract base class for simplex search algorithms."""

    def __init__(self, problem,
                 initial_simplex,
                 max_iterations=float("inf"),
                 xtol=None,
                 ftol=None,
                 shrink_factor=0.5,
                 individual_factory=None,
                 sort_key=None,
                 verbosity=1,
                 **kwargs):
        """Constructor.

        Parameters
        ----------
        problem : optproblems.Problem
            An optimization problem.
        initial_simplex : list
            The points or individuals of the initial simplex.
        max_iterations : int, optional
            A potential budget restriction on the number of iterations.
            Default is unlimited.
        xtol : float, optional
            The algorithm stops when the maximal absolute deviation in all
            dimensions of the search space between the best and all other
            points in the simplex drops below this value. By default,
            this criterion is off.
        ftol : float, optional
            The algorithm stops when the absolute difference of objective
            values between the best and worst individual in the simplex
            drops below this value. This criterion can only be used with
            scalar objective values. By default, this criterion is off.
        shrink_factor : float, optional
            The parameter for the shrink operation.
        individual_factory : callable, optional
            A callable taking a point as argument. It must return an object
            with two member attributes `phenome` and `objective_values`. The
            `phenome` contains the solution, while `objective_values` is set
            to None. By default, :class:`optproblems.base.Individual` is
            used.
        sort_key : callable, optional
            A sort key for ranking the individuals in the simplex. By
            default, :func:`dfoalgos.base.lexicographic_sort_key` is used.
        verbosity : int, optional
            A value of 0 means quiet, 1 means some information is printed
            to standard out on start and termination of this algorithm.

        """
        Observable.__init__(self)
        self.problem = problem
        initial_simplex = list(initial_simplex)
        self.max_iterations = max_iterations
        self.xtol = xtol
        self.ftol = ftol
        assert shrink_factor > 0.0 and shrink_factor < 1.0
        self.shrink_factor = shrink_factor
        if individual_factory is None:
            individual_factory = Individual
        self.individual_factory = individual_factory
        for i, element in enumerate(initial_simplex):
            individual_score = hasattr(element, "phenome")
            individual_score += hasattr(element, "objective_values")
            if individual_score == 0:
                element = individual_factory(element)
            elif individual_score != 2:
                message = "don't know how to treat simplex element "
                raise Exception(message + str(element))
            element.age = 1
            initial_simplex[i] = element
        self.simplex = initial_simplex
        self.prev_simplex_points = None
        if sort_key is None:
            sort_key = lexicographic_sort_key
        self.sort_key = sort_key
        self.verbosity = verbosity
        self.iteration = 0
        self.remaining_iterations = max_iterations
        self.last_termination = None
        self.offspring = []
        self.num_expansion_failures = 0
        self.num_expansions = 0
        self.num_outside_failures = 0
        self.num_outside_operations = 0
        self.num_reorientations = 0
        self.reoriented = False
        self.num_shrinks = 0
        if kwargs and verbosity:
            str_kwargs = ", ".join(map(str, kwargs.keys()))
            print("Warning: SimplexSearch.__init__() got unexpected keyword arguments " + str_kwargs)


    @classmethod
    def minimize(cls, fun,
                 x0,
                 args=(),
                 bounds=None,
                 callback=None,
                 options=None,
                 **kwargs):
        """Minimization of scalar function of one or more variables.

        This function mimics the SciPy interface for optimizers.

        Parameters
        ----------
        fun : callable
            Objective function.
        x0 : sequence
            Initial guess.
        args : tuple, optional
            Extra arguments passed to the objective function.
        bounds : sequence, optional
            Bounds for variables. ``(min, max)`` pairs for each element in
            ``x``, defining the bounds on that parameter. Use None for one of
            ``min`` or ``max`` when there is no bound in that direction.
        callback : callable, optional
            Called after each iteration, as ``callback(xk)``, where ``xk`` is
            the current parameter vector.
        options : dict, optional
            A dictionary of solver options. The following generic options are
            accepted:

                maxiter : int
                    Maximum number of iterations to perform.
                disp : bool
                    Set to True to print convergence messages.

        Returns
        -------
        result : OptimizeResult
            The optimization result represented as a ``OptimizeResult`` object.
            Important attributes are: ``x`` the solution array, ``success`` a
            Boolean flag indicating if the optimizer exited successfully and
            ``message`` which describes the cause of the termination.

        """
        def wrapper_function(phenome):
            return fun(phenome, *args)

        def observer(algo):
            best_ind = min(algo.simplex, key=algo.sort_key)
            try:
                phenome = repair(best_ind.phenome)
            except:
                phenome = best_ind.phenome
            callback(phenome)

        dim = len(x0)
        try:
            obj_function_name = fun.__name__
        except AttributeError:
            obj_function_name = str(fun)
        problem_name = "Problem(" + obj_function_name + ")"
        if bounds is not None:
            min_bounds = [min_bound for min_bound, _ in bounds]
            max_bounds = [max_bound for _, max_bound in bounds]
            unit_cube = ([0.0] * dim, [1.0] * dim)
            scale_to_orig = ScalingPreprocessor(from_cuboid=unit_cube,
                                                to_cuboid=(min_bounds, max_bounds))
            scale_to_unit = ScalingPreprocessor(from_cuboid=(min_bounds, max_bounds),
                                                to_cuboid=unit_cube)
            repair = BoundConstraintsRepair((min_bounds, max_bounds),
                                            ["reflection"] * dim,
                                            previous_preprocessor=scale_to_orig)
            problem = Problem(wrapper_function,
                              phenome_preprocessor=repair,
                              name=problem_name)
            initial_simplex = create_tilted_regular_simplex(scale_to_unit(x0),
                                                            size_param=1.0)
        else:
            problem = Problem(wrapper_function, name=problem_name)
            initial_simplex = create_tilted_regular_simplex(x0)
        if options is not None and "maxiter" in options:
            kwargs["max_iterations"] = options["maxiter"]
        try:
            kwargs["max_iterations"] = kwargs["maxiter"]
        except KeyError:
            pass
        if options is not None and "disp" in options:
            kwargs["verbosity"] = int(options["disp"])
        try:
            kwargs["verbosity"] = int(kwargs["disp"])
        except KeyError:
            pass
        algo = cls(problem, initial_simplex, **kwargs)
        if callback is not None:
            algo.attach(observer)
        algo.run()
        result = OptimizeResult()
        best_individual = min(algo.simplex, key=algo.sort_key)
        if bounds is None:
            result.x = best_individual.phenome
        else:
            result.x = repair(best_individual.phenome)
        result.message = str(algo.last_termination)
        result.fun = best_individual.objective_values
        result.nfev = problem.consumed_evaluations
        result.nit = algo.iteration
        return result


    def __str__(self):
        """Return the algorithm's name."""
        return self.__class__.__name__


    @staticmethod
    def calc_mean_point(individuals):
        """Calculate the mean point for reflection."""
        phenomes = [ind.phenome for ind in individuals]
        return center_of_mass(phenomes)


    def update_simplex(self, new_simplex):
        """Overwrite the current simplex with a new one.

        Parameters
        ----------
        new_simplex : list of Individual
            The new solutions.

        """
        self.simplex = new_simplex


    def scale(self, individuals, fixed_ind, factor):
        """Scale individuals by a given factor.

        This method unwraps the points, delegates to :func:`scale`, and
        then again wraps the scaled points in individuals with the
        individual factory.

        Parameters
        ----------
        individuals : iterable of Individual
            The individuals containing the points to scale.
        fixed_ind : Individual
            The individual containing the fixed point of the transformation.
        factor : float
            The scale factor.

        Returns
        -------
        scaled_individuals : list of Individual
            List containing scaled individuals.

        """
        individual_factory = self.individual_factory
        points = [ind.phenome for ind in individuals]
        fixed_point = fixed_ind.phenome
        scaled_points = scale(points, fixed_point, factor)
        return [individual_factory(p) for p in scaled_points]


    def shrink_operation(self):
        """Carry out the shrink operation.

        Returns
        -------
        fail : bool
            If the operation was unsuccessful.

        """
        shrunk_individuals = self.scale(self.simplex[1:],
                                        self.simplex[0],
                                        self.shrink_factor)
        self.offspring.extend(shrunk_individuals)
        self.problem.batch_evaluate(shrunk_individuals)
        self.update_simplex([self.simplex[0]] + shrunk_individuals)
        self.num_shrinks += 1


    def displace_operation(self, reference_sort_key,
                           mean_point,
                           worst_point,
                           factor):
        """Carry out a displacement operation of a single point.

        Parameters
        ----------
        reference_sort_key : float or iterable
            Comparison to this reference sort key determines if the
            operation was successful.
        mean_point : iterable
            Normally the mean of all points in the simplex except for the
            worst one.
        worst_point : iterable
            The worst point in the simplex, which is to be displaced.
        factor : float
            Determines how far the worst point is displaced.

        Returns
        -------
        fail : bool
            If the operation was unsuccessful.

        """
        new_point = displace(mean_point, worst_point, factor)
        new_individual = self.individual_factory(new_point)
        self.offspring.append(new_individual)
        self.problem.evaluate(new_individual)
        if self.sort_key(new_individual) <= reference_sort_key:
            self.simplex[-1] = new_individual
            self.update_simplex(self.simplex)
            fail = False
        else:
            fail = True
        return fail


    def run(self):
        """Run the algorithm.

        The :func:`step<dfoalgos.simplex.SimplexSearch.step>` function is
        called in a loop. The algorithm stops when a :class:`StopIteration`
        exception is caught or when the stopping criterion evaluates to
        True.

        Returns
        -------
        best_individual : Individual
            The best individual of the simplex according to the sort key.

        """
        # shortcuts
        stopping_criterion = self.stopping_criterion
        step = self.step
        if self.verbosity > 0:
            print(str(self) + " running on problem " + str(self.problem))
        try:
            unevaluated = []
            for individual in self.simplex:
                if individual.objective_values is None:
                    unevaluated.append(individual)
            self.problem.batch_evaluate(unevaluated)
            while not stopping_criterion():
                step()
        except StopIteration as instance:
            self.last_termination = instance
            if self.verbosity > 0:
                print(instance)
        if self.verbosity > 0:
            print("Algorithm terminated")
        min_candidates = []
        for ind in self.simplex + self.offspring:
            if ind.objective_values is not None:
                min_candidates.append(ind)
        return min(min_candidates, key=self.sort_key)


    def stopping_criterion(self):
        """Check if optimization should go on.

        The algorithm halts when this method returns True or raises an
        exception.

        Raises
        ------
        ResourcesExhausted
            when number of iterations reaches maximum
        Stalled
            when the `xtol` or `ftol` criteria trigger or the simplex
            contains a duplicate point

        """
        if self.remaining_iterations <= 0:
            raise ResourcesExhausted("iterations")
        simplex = self.simplex
        simplex.sort(key=self.sort_key)
        num_individuals = len(simplex)
        xtol = self.xtol
        if xtol is not None:
            best_phenome = simplex[0].phenome
            max_diff = 0.0
            for i, individual in enumerate(simplex, 1):
                for phene, best_phene in zip(individual.phenome, best_phenome):
                    diff = abs(phene - best_phene)
                    if diff > max_diff:
                        max_diff = diff
            if max_diff <= xtol:
                raise Stalled("xtol")
        ftol = self.ftol
        if ftol is not None:
            best_objective = simplex[0].objective_values
            max_diff = 0.0
            for i, individual in enumerate(simplex, 1):
                diff = abs(individual.objective_values - best_objective)
                if diff > max_diff:
                    max_diff = diff
            if max_diff <= ftol:
                raise Stalled("ftol")
        phenomes = [ind.phenome for ind in simplex]
        if phenomes == self.prev_simplex_points:
            raise Stalled("unmodified simplex")
        self.prev_simplex_points = phenomes
        if xtol is None and ftol is None:
            for i, phenome in enumerate(phenomes):
                for j in range(i + 1, num_individuals):
                    if phenome == phenomes[j]:
                        raise Stalled("collapsed simplex")
        return False


    def step(self):
        """Perform one optimization step.

        This is an abstract method. Overwrite in your own simplex search
        implementation.

        """
        raise NotImplementedError()



class SpendleySimplexSearch(SimplexSearch):
    """Fixed-shape, variable-size simplex search.

    This algorithm is regarded as the oldest simplex search around. It was
    introduced by [Spendley1962]_, who were also the first to propose the
    basic reflection operation. This implementation follows the description
    of [Gurson2000]_ (pp. 13-23), which extends the original algorithm with
    a shrink operation and generalizes it to more than two dimensions.

    References
    ----------
    .. [Spendley1962] W. Spendley, G. R. Hext, and F. R. Himsworth (1962).
        Sequential Application of Simplex Designs in Optimisation and
        Evolutionary Operation. Technometrics, Vol. 4, No. 4, pp. 441-461.
    .. [Gurson2000] Adam P. Gurson (2000). Simplex Search Behavior in
        Nonlinear Optimization. Honors thesis.
        http://www.cs.wm.edu/~va/CS495/gurson.pdf

    """
    def __init__(self, problem,
                 initial_simplex,
                 max_age=None,
                 **kwargs):
        """Constructor.

        Parameters
        ----------
        problem : optproblems.Problem
            An optimization problem.
        initial_simplex : list
            The points of the initial simplex.
        max_age : int, optional
            A shrink operation is triggered when the best individual's age
            reaches `max_age`. The default is ``len(initial_simplex)``.
        kwargs
            Arbitrary keyword arguments, passed to the super class.

        """
        SimplexSearch.__init__(self, problem, initial_simplex, **kwargs)
        if max_age is None:
            max_age = len(initial_simplex)
        self.max_age = max_age
        self.previous_new_ind = None


    def step(self):
        """Perform one optimization step."""
        self.offspring = []
        individual_factory = self.individual_factory
        sort_key = self.sort_key
        self.simplex.sort(key=sort_key)
        # potential shrink
        if self.simplex[0].age > self.max_age:
            self.shrink_operation()
            self.simplex.sort(key=sort_key)
            for ind in self.simplex:
                ind.age = 1
        # determine point to reflect
        if self.simplex[-1] is self.previous_new_ind:
            point_to_reflect = self.simplex[-2].phenome
            replace_index = -2
            remaining_simplex = self.simplex[:-2] + [self.simplex[-1]]
        else:
            point_to_reflect = self.simplex[-1].phenome
            replace_index = -1
            remaining_simplex = self.simplex[:-1]
        # reflect
        mean_point = self.calc_mean_point(remaining_simplex)
        new_point = displace(mean_point, point_to_reflect, 1.0)
        new_individual = individual_factory(new_point)
        self.offspring.append(new_individual)
        self.problem.evaluate(new_individual)
        self.simplex[replace_index] = new_individual
        # update ages
        if sort_key(new_individual) < sort_key(self.simplex[0]):
            for ind in self.simplex:
                ind.age = 1
        else:
            new_individual.age = 0
            for ind in self.simplex:
                ind.age += 1
        self.update_simplex(self.simplex)
        self.previous_new_ind = new_individual
        self.notify_observers()
        self.iteration += 1
        self.remaining_iterations -= 1



class NelderMeadSimplexSearch(SimplexSearch):
    """The simplex search by Nelder and Mead.

    This algorithm was proposed by [Nelder1965]_. It adapts the simplex
    shape to the landscape by expansion and contration operations. This
    algorithm is fast also on ill-conditioned problems, but may converge to
    a non-stationary point.

    References
    ----------
    .. [Nelder1965] Nelder, J.A. and Mead, R. (1965). A simplex method for
        function minimization, The Computer Journal, Vol. 7, No. 4,
        pp. 308-313. https://dx.doi.org/10.1093/comjnl/7.4.308

    """
    def __init__(self, problem,
                 initial_simplex,
                 reflection_factor=1.0,
                 expansion_factor=2.0,
                 contraction_factor=0.5,
                 **kwargs):
        """Constructor.

        Parameters
        ----------
        problem : optproblems.Problem
            An optimization problem.
        initial_simplex : list
            The points of the initial simplex.
        reflection_factor : float, optional
            The parameter used for reflection.
        expansion_factor : float, optional
            The parameter used for expansion.
        contraction_factor : float, optional
            The parameter used for inside and outside contraction.
        kwargs
            Arbitrary keyword arguments, passed to the super class.

        """
        SimplexSearch.__init__(self, problem, initial_simplex, **kwargs)
        assert reflection_factor > 0.0
        assert expansion_factor >= 1.0
        assert contraction_factor > 0.0 and contraction_factor < 1.0
        self.reflection_factor = reflection_factor
        self.expansion_factor = expansion_factor
        self.contraction_factor = contraction_factor


    def step(self):
        """Perform one optimization step."""
        update_simplex = self.update_simplex
        displace_operation = self.displace_operation
        self.offspring = []
        individual_factory = self.individual_factory
        sort_key = self.sort_key
        self.simplex.sort(key=sort_key)
        worst_point = self.simplex[-1].phenome
        problem = self.problem
        refl_factor = self.reflection_factor
        cont_factor = self.contraction_factor
        # reflect
        mean_point = self.calc_mean_point(self.simplex[:-1])
        new_individual = individual_factory(displace(mean_point,
                                                     worst_point,
                                                     refl_factor))
        self.offspring.append(new_individual)
        problem.evaluate(new_individual)
        new_sort_key = sort_key(new_individual)
        do_shrink = False
        if new_sort_key < sort_key(self.simplex[0]) and self.expansion_factor > 1.0:
            fail = displace_operation(new_sort_key,
                                      mean_point,
                                      worst_point,
                                      refl_factor * self.expansion_factor)
            if fail:
                self.simplex[-1] = new_individual
                update_simplex(self.simplex)
                self.num_expansion_failures += fail
            self.num_expansions += 1
        elif new_sort_key < sort_key(self.simplex[-2]):
            # new point is not the worst in the new simplex
            # => next iteration
            self.simplex[-1] = new_individual
            update_simplex(self.simplex)
        else:
            worst_key = sort_key(self.simplex[-1])
            if new_sort_key < worst_key:
                # outside contraction
                fail = displace_operation(new_sort_key,
                                          mean_point,
                                          worst_point,
                                          refl_factor * cont_factor)
                self.num_outside_failures += fail
            else:
                # inside contraction
                fail = displace_operation(worst_key,
                                          mean_point,
                                          worst_point,
                                          -cont_factor)
            do_shrink = fail
        if do_shrink:
            self.shrink_operation()
        self.notify_observers()
        self.iteration += 1
        self.remaining_iterations -= 1



class NMKSimplexSearch(NelderMeadSimplexSearch):
    """Nelder-Mead simplex search with reorientations by Kelley.

    This algorithm employs a sufficient decrease condition to detect
    stagnation and convergence to a non-stationary point. If not fulfilled,
    the simplex is reinitialized, based on information from the simplex
    gradient. Thus, this algorithm is unfortunately not rank-based.
    For details see [Kelley1999]_.

    References
    ----------
    .. [Kelley1999] C. T. Kelley (1999). Detection and Remediation of
        Stagnation in the Nelder-Mead Algorithm Using a Sufficient Decrease
        Condition, SIAM Journal on Optimization, 10:1, pp. 43-55.
        https://doi.org/10.1137/S1052623497315203

    """
    def __init__(self, problem,
                 initial_simplex,
                 max_num_reorientations=None,
                 recalc_alpha=True,
                 alpha0=1e-4,
                 **kwargs):
        """Constructor.

        Parameters
        ----------
        problem : optproblems.Problem
            An optimization problem.
        initial_simplex : list
            The points of the initial simplex.
        max_num_reorientations : int, optional
            The maximal number of allowed reorientations before giving up.
        recalc_alpha : bool, optional
            This flag decides if alpha is recalculated after reorientations.
        alpha0 : float, optional
            A coefficient for the calculation of alpha.
        kwargs
            Arbitrary keyword arguments, passed to the super class.

        """
        NelderMeadSimplexSearch.__init__(self, problem,
                                         initial_simplex,
                                         **kwargs)
        self.max_num_reorientations = max_num_reorientations
        self.recalc_alpha = recalc_alpha
        self.alpha = None
        self.alpha0 = alpha0


    def step(self):
        """Perform one optimization step."""
        dim = len(self.simplex) - 1
        update_simplex = self.update_simplex
        displace_operation = self.displace_operation
        self.offspring = []
        individual_factory = self.individual_factory
        sort_key = self.sort_key
        self.simplex.sort(key=sort_key)
        worst_point = self.simplex[-1].phenome
        problem = self.problem
        refl_factor = self.reflection_factor
        cont_factor = self.contraction_factor
        # data needed for potential reorientation
        avg_obj_value = np.mean([ind.objective_values for ind in self.simplex])
        obj_deltas = np.array([ind.objective_values for ind in self.simplex[1:]])
        obj_deltas -= self.simplex[0].objective_values
        direction_vectors = np.array([ind.phenome for ind in self.simplex[1:]])
        direction_vectors -= self.simplex[0].phenome
        oriented_lengths = [np.linalg.norm(vec, ord=2) for vec in direction_vectors]
        try:
            simplex_gradient = np.linalg.solve(direction_vectors, obj_deltas)
            norm = np.linalg.norm(simplex_gradient, ord=2)
            if self.alpha is None or (self.recalc_alpha and self.reoriented):
                self.alpha = self.alpha0 * max(oriented_lengths) / norm
        except np.linalg.linalg.LinAlgError as exception:
            raise Aborted(str(exception) + " in simplex gradient computation")
        # reflect
        mean_point = self.calc_mean_point(self.simplex[:-1])
        new_individual = individual_factory(displace(mean_point,
                                                     worst_point,
                                                     refl_factor))
        self.offspring.append(new_individual)
        problem.evaluate(new_individual)
        new_sort_key = sort_key(new_individual)
        do_shrink = False
        if new_sort_key < sort_key(self.simplex[0]) and self.expansion_factor > 1.0:
            fail = displace_operation(new_sort_key,
                                      mean_point,
                                      worst_point,
                                      refl_factor * self.expansion_factor)
            if fail:
                self.simplex[-1] = new_individual
                update_simplex(self.simplex)
                self.num_expansion_failures += fail
            self.num_expansions += 1
        elif new_sort_key < sort_key(self.simplex[-2]):
            # new point is not the worst in the new simplex
            # => next iteration
            self.simplex[-1] = new_individual
            update_simplex(self.simplex)
        else:
            worst_key = sort_key(self.simplex[-1])
            if new_sort_key < worst_key:
                # outside contraction
                fail = displace_operation(new_sort_key,
                                          mean_point,
                                          worst_point,
                                          refl_factor * cont_factor)
                self.num_outside_failures += fail
            else:
                # inside contraction
                fail = displace_operation(worst_key,
                                          mean_point,
                                          worst_point,
                                          -cont_factor)
            do_shrink = fail
        # check sufficient decrease condition
        new_avg_obj = np.mean([ind.objective_values for ind in self.simplex])
        decrease = avg_obj_value - new_avg_obj
        if decrease < self.alpha * np.sum(simplex_gradient ** 2) / dim:
            # decrease is not sufficient
            max_reor = self.max_num_reorientations
            num_reor = self.num_reorientations
            reor_allowed = max_reor is None or max_reor < 0 or num_reor < max_reor
            if not reor_allowed:
                raise Stalled("max number of reorientations")
            min_oriented_length = min(oriented_lengths)
            new_offsets = np.sign(simplex_gradient)
            # set sign of zero elements to positive
            new_offsets = np.sign(0.5 + new_offsets)
            new_simplex = [self.simplex[0]]
            best_phenome = self.simplex[0].phenome
            for i, offset in enumerate(new_offsets):
                point = best_phenome[:]
                point[i] -= min_oriented_length * offset
                new_simplex.append(self.individual_factory(point))
            update_simplex(new_simplex)
            self.num_reorientations += 1
            self.reoriented = True
            do_shrink = True
        else:
            self.reoriented = False
        if do_shrink:
            self.shrink_operation()
        self.notify_observers()
        self.iteration += 1
        self.remaining_iterations -= 1



def ANMSimplexSearch(problem,
                     initial_simplex,
                     nelder_mead_class,
                     **kwargs):
    """Factory method to produce a Nelder-Mead instance with adaptive parameters.

    Expansion, contraction, and shrink factor are chosen dimension-dependent,
    as proposed in [Gao2012]_. These settings have been shown to perform
    better than the default parametrization on high-dimensional problems.

    Parameters
    ----------
    problem : optproblems.Problem
        An optimization problem.
    initial_simplex : list
        The points of the initial simplex.
    nelder_mead_class : class
        The class that shall be instantiated.
    kwargs
        Arbitrary keyword arguments, passed to the constructor of
        `nelder_mead_class`.

    Returns
    -------
    instance : NelderMeadSimplexSearch
        An instance of the given simplex search algorithm.

    References
    ----------
    .. [Gao2012] Fuchang Gao; Lixing Han (2012). Implementing the Nelder-Mead
        simplex algorithm with adaptive parameters. Computational Optimization
        and Applications, Volume 51, Issue 1, pp 259–277.
        https://doi.org/10.1007/s10589-010-9329-3

    """
    dim = len(initial_simplex[0])
    instance = nelder_mead_class(problem,
                                 initial_simplex,
                                 reflection_factor=1.0,
                                 expansion_factor=1.0 + 2.0 / dim,
                                 contraction_factor=0.75 - 1.0 / (2 * dim),
                                 shrink_factor=1.0 - 1.0 / dim,
                                 **kwargs)
    return instance
