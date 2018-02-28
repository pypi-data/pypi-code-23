
import sys
import math

from optproblems.base import ResourcesExhausted, Individual, Stalled

from dfoalgos.base import Observable, lexicographic_sort_key, rank



def approx_gradient(position, obj_at_pos, function, step_size):
    """Approximate gradient with forward differences.

    Parameters
    ----------
    position : list
        The position where the gradient is approximated.
    obj_at_pos : float
        The objective value at this position (to save one evaluation).
    function : callable
        The objective function.
    step_size : float
        Step size for each dimension.

    Returns
    -------
    grad : list
        Approximated gradient.

    """
    dim = len(position)
    grad = [0.0] * dim
    for i in range(dim):
        offset_point = list(position)
        offset_point[i] += step_size
        quotient = (function(offset_point) - obj_at_pos) / step_size
        grad[i] = quotient
    return grad



class RankGradientDescentMethod(Observable):
    """

    """
    def __init__(self, problem,
                 start_point,
                 step_size,
                 shrink_factor=0.5,
                 grad_mode="forward",
                 grad_step_size="reuse_step_size",
                 consider_numerical_diff_points=False,
                 max_iterations=float("inf"),
                 xtol=None,
                 ftol=None,
                 individual_factory=None,
                 sort_key=None,
                 verbosity=1):
        """Constructor.

        Parameters
        ----------
        problem : optproblems.Problem
            An optimization problem.
        start_point : list
            The starting point for the optimization.
        step_size : float
            The initial step size.
        shrink_factor : float, optional
            This value must be larger than 0 and smaller than 1. It is
            multiplied with the step size in iterations where no
            improvement is found.
        grad_mode: str, optional
            Determines how to compute numerical differences. Options are
            "forward", and "symmetric".
        grad_step_size : float or str, optional
            Determines the step size used for computing the numerical
            differences. "reuse_step_size" means the same step size as for
            optimization is used. "adaptive" means that for each dimension
            ``sqrt(eps) * x`` is used, where eps is the machine precision
            and x is the decision variable. Numeric values are used as
            provided.
        consider_numerical_diff_points : bool, optional
            Determines if the points used to compute the numerical
            differences shall be also considered as potential improvements
            of the current solution, or if only the point of the gradient
            descent shall be considered.
        max_iterations : int, optional
            A potential budget restriction on the number of iterations.
            Default is unlimited.
        xtol : float, optional
            The algorithm stops when the step size drops below this value.
            By default, this criterion is off.
        ftol : float, optional
            The algorithm stops when the absolute difference of objective
            values between the best individual and the worst of the last
            evaluated solutions drops below this value. When forward
            differences are used, the last n solutions are
            considered, when symmetric differences are used, 2n solutions
            are considered. This criterion can only be used with scalar
            objective values. By default, this criterion is off.
        individual_factory : callable, optional
            A callable taking a point as argument. It must return an object
            with two member attributes `phenome` and `objective_values`. The
            `phenome` contains the solution, while `objective_values` is set
            to None. By default, :class:`optproblems.base.Individual` is
            used.
        sort_key : callable, optional
            A sort key for ranking the individuals. By default,
            :func:`dfoalgos.base.lexicographic_sort_key` is used.
        verbosity : int, optional
            A value of 0 means quiet, 1 means some information is printed
            to standard out on start and termination of this algorithm.

        """
        Observable.__init__(self)
        self.problem = problem
        assert step_size > 0.0
        self.step_size = step_size
        assert shrink_factor > 0.0 and shrink_factor < 1.0
        self.shrink_factor = shrink_factor
        assert grad_mode in ("forward", "symmetric")
        self.grad_mode = grad_mode
        self.grad_step_size = grad_step_size
        self.consider_numerical_diff_points = consider_numerical_diff_points
        self.remaining_iterations = max_iterations
        self.xtol = xtol
        self.ftol = ftol
        if individual_factory is None:
            individual_factory = Individual
        self.individual_factory = individual_factory
        self.best_individual = individual_factory(start_point)
        if sort_key is None:
            sort_key = lexicographic_sort_key
        self.sort_key = sort_key
        self.grad_norm = float("inf")
        self.verbosity = verbosity
        self.iteration = 0
        self.last_termination = None
        self.improvement_found = False
        self.prev_improvement_found = False
        self.offspring = []
        self.prev_offspring = []
        self.num_shrinks = 0


    def __str__(self):
        """Return the algorithm's name."""
        return self.__class__.__name__


    def run(self):
        """Run the algorithm.

        The :func:`step<dfoalgos.pattern.PatternSearch.step>` function is
        called in a loop. The algorithm stops when a :class:`StopIteration`
        exception is caught or when the stopping criterion evaluates to
        True.

        Returns
        -------
        best_individual : Individual
            The best individual found so far, according to the sort key.

        """
        # shortcuts
        stopping_criterion = self.stopping_criterion
        step = self.step
        if self.verbosity > 0:
            print(str(self) + " running on problem " + str(self.problem))
        try:
            if self.best_individual.objective_values is None:
                self.problem.evaluate(self.best_individual)
            while not stopping_criterion():
                step()
        except StopIteration as instance:
            self.last_termination = instance
            if self.verbosity > 0:
                print(instance)
        if self.verbosity > 0:
            print("Algorithm terminated")
        min_candidates = [self.best_individual]
        for ind in self.offspring:
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

        """
        if self.remaining_iterations <= 0:
            raise ResourcesExhausted("iterations")
        if self.xtol is not None and self.step_size <= self.xtol:
            raise Stalled("xtol")
        ftol = self.ftol
        if ftol is not None and len(self.offspring) > 0:
            best_objective = self.best_individual.objective_values
            max_diff = 0.0
            for individual in self.offspring:
                diff = abs(individual.objective_values - best_objective)
                if diff > max_diff:
                    max_diff = diff
            if max_diff <= ftol:
                raise Stalled("ftol")
        return False


    def update_best_individual(self, new_best):
        """Set a new current best individual.

        The success is also marked by setting `improvement_found` to True.

        """
        self.best_individual = new_best
        self.improvement_found = True


    def gradient_function(self, pos_individual):
        """Approximate gradient with numerical differences.

        Parameters
        ----------
        pos_individual : Individual
            The position where the gradient is approximated.

        Returns
        -------
        grad : list
            Approximated gradient.

        """
        individual_factory = self.individual_factory
        dim = len(pos_individual.phenome)
        step_size = self.grad_step_size
        if step_size is None or step_size == "adaptive":
            sqrt_eps = math.sqrt(sys.float_info.epsilon)
            step_sizes = []
            for x in pos_individual.phenome:
                if x != 0.0:
                    step = sqrt_eps * x
                else:
                    step = sys.float_info.epsilon
                step_sizes.append(step)
            mean_step = math.fsum(step_sizes) / float(dim)
        elif step_size == "reuse_step_size":
            step_sizes = [self.step_size] * dim
            mean_step = self.step_size
        else:
            step_sizes = [step_size] * dim
            mean_step = step_size
        mode = self.grad_mode
        grad = [0.0] * dim
        individuals = []
        for i in range(dim):
            offset_point = list(pos_individual.phenome)
            offset_point[i] += step_sizes[i]
            individuals.append(individual_factory(offset_point))
            if mode == "symmetric":
                offset_point = list(pos_individual.phenome)
                offset_point[i] -= step_sizes[i]
                individuals.append(individual_factory(offset_point))
        # try to find reusable objective values
        unevaluated = []
        for ind in individuals:
            for prev_ind in self.prev_offspring:
                if prev_ind.phenome == ind.phenome:
                    ind.objective_values = prev_ind.objective_values
                    break
            if ind.objective_values is None:
                unevaluated.append(ind)
        self.offspring.extend(individuals)
        self.problem.batch_evaluate(unevaluated)
        individuals.append(pos_individual)
        ranks = rank(individuals, self.sort_key)
        if mode == "forward":
            for i in range(dim):
                quotient = (ranks[i] - ranks[-1]) * mean_step / step_sizes[i]
                grad[i] = quotient
        elif mode == "symmetric":
            for i in range(dim):
                quotient = (ranks[2*i] - ranks[2*i+1]) * mean_step / step_sizes[i]
                grad[i] = quotient
        else:
            raise Exception("unknown numerical differentiation mode: " + str(mode))
        return grad


    def descent_step(self, pos_individual, step_size=None):
        """Do a small step in a supposed descent direction.

        Parameters
        ----------
        pos_individual : Individual
            The position where the gradient is approximated.
        step_size : float
            Step size for each dimension.

        Returns
        -------
        proposed_point : list
            A point which is hopefully an improvement.
        norm : float
            The length of the gradient vector.

        """
        gradient = self.gradient_function(pos_individual)
        norm = math.sqrt(math.fsum(g ** 2 for g in gradient))
        step_vector = [step_size * g / norm for g in gradient]
        position = pos_individual.phenome
        proposed_point = [p - s for p, s in zip(position, step_vector)]
        return self.individual_factory(proposed_point), norm


    def step(self):
        """Perform one optimization step.

        Raises
        ------
        Stalled
            when the generated point does not differ from the current best
            solution or the norm of the gradient has become zero

        """
        self.prev_improvement_found = self.improvement_found
        self.prev_offspring = self.offspring
        # reset attributes
        self.improvement_found = False
        self.offspring = []
        step_size = self.step_size
        try:
            candidate, self.grad_norm = self.descent_step(self.best_individual,
                                                          step_size)
        except ZeroDivisionError:
            # the norm of the gradient may become zero
            # use this as stopping criterion
            raise Stalled("norm of gradient has become zero")
        if candidate.phenome == self.best_individual.phenome:
            # stop because no new point is generated any more
            # (probably because step size is too small)
            raise Stalled("new point is equal to current")
        self.problem.evaluate(candidate)
        if self.sort_key(candidate) < self.sort_key(self.best_individual):
            self.update_best_individual(candidate)
        if self.consider_numerical_diff_points:
            for ind in self.offspring:
                if self.sort_key(ind) < self.sort_key(self.best_individual):
                    self.update_best_individual(ind)
        self.notify_observers()
        if not self.improvement_found:
            self.step_size *= self.shrink_factor
            self.num_shrinks += 1
        self.iteration += 1
        self.remaining_iterations -= 1
