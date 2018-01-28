"""
PSO stand for Particle Swarm Optimization. A metaheuristic optimize method
based on how particles in a swarm looking for food. For more please read
https://viisix.space/algorijs/01-particles-swarm-optimization/
"""

from copy import deepcopy
from .optimization import AlgorithmObject, OptimizationMixin
from .utils import is_better


class Particle(OptimizationMixin):
    """Particles of the swarm. Each particle has its own position and velocity.
    Every iteration step, each particle will try to move to different location
    base on local and global best."""

    def __init__(self, optimization_object, learning_factors):
        """

        :param optimization_object: Initialized Optimization object passed
        from PSO object.
        :type optimization_object: PyOptCollection.optimization.Optimization
        :param learning_factors: Local and global learning factors.
        :type learning_factors: tuple
        """
        self.optimization_object = optimization_object
        self.learning_factors = learning_factors

        self.position = [0.0] * self.no_dimensions
        self.velocity = [0.0] * self.no_dimensions
        self._spawn()
        while not self._check_constraint():
            self._spawn()

        self.value = self.optimization_object.func(self.position)
        self.best = (self.value, deepcopy(self.position))

    def update(self, global_best):
        """
        Update velocity and position of the particle. New position must match
        with all constraints of the optimization.

        :param global_best: Global best from the last iteration step.
        :return: None
        """
        self._update_velocity(global_best)

        next_position = self._get_new_position()

        loop_count = 0
        while not self._check_constraint(next_position):
            if loop_count < 5:
                self._resize_velocity(0.5)
                loop_count += 1
            else:
                self._spawn(position=False)
            next_position = self._get_new_position()

        self.position = next_position
        self.value = self.optimization_object.func(self.position)
        if is_better(self.best[0], self.value,
                     self.optimization_object.find_max):
            self.best = (self.value, deepcopy(self.position))

    def _check_constraint(self, position=None):
        if position is None:
            return self.optimization_object.check_constraints(self.position)
        return self.optimization_object.check_constraints(position)

    def _spawn(self, position=True, velocity=True):
        for dim in range(self.no_dimensions):
            if position:
                self.position[dim] = \
                    self.random_generator.uniform(
                        self.boundaries[dim][0],
                        self.boundaries[dim][1]
                    )
            if velocity:
                self.velocity[dim] = \
                    (self.random_generator.random() - 0.5) * \
                    max(self.learning_factors)

    def _get_new_position(self):
        new_position = [0.0] * self.no_dimensions
        for dim in range(self.optimization_object.no_dimensions):
            new_position[dim] = self.position[dim] + self.velocity[dim]

        return new_position

    def _update_velocity(self, global_best):
        r_1 = self.random_generator.random()
        r_2 = self.random_generator.random()

        for dim in range(self.no_dimensions):
            d_v1 = self.learning_factors[0] * r_1 * \
                (self.best[1][dim] - self.position[dim])
            d_v2 = self.learning_factors[1] * r_2 * \
                (global_best[1][dim] - self.position[dim])

            self.velocity[dim] = self.velocity[dim] + d_v1 + d_v2

    def _resize_velocity(self, factor):
        for dim in range(self.no_dimensions):
            self.velocity[dim] *= factor


class PSO(AlgorithmObject):
    """This class will be the AlgorithmObject for PSO."""

    def __init__(self, optimization_object, **kwargs):
        """

        :param optimization_object: Initialized Optimization object.
        :type optimization_object: PyOptCollection.optimization.Optimization
        :param no_particles: Total number of particles inside the swarm.
        :type no_particles: int
        :param no_iteration_steps: Total number of iteration steps.
        :type no_iteration_steps: int
        :param c_1: Local learning factor, default is 2.0.
        :type c_1: float
        :param c_2: Global learning factor, default is 2.0.
        :type c_2: float
        :param kwargs:
        """

        AlgorithmObject.__init__(self, optimization_object, **kwargs)
        self.learning_factors = \
            (kwargs.get('c_1', 2.0), kwargs.get('c_2', 2.0))
        self.no_particles = kwargs.get('no_particles', 10)
        self.no_iteration_steps = kwargs.get('no_iteration_steps', 50)

        self.particles = list()

    def solve(self):
        current_iter_steps = 0
        self._spawn_particles()
        if self.verbose:
            print("Iteration step #%d, best value: %s" % (
                current_iter_steps, self.best
            ))

        current_iter_steps += 1
        while current_iter_steps < self.no_iteration_steps:
            self._pso_do_iter()
            if self.verbose:
                print("Iteration step #%d, best value: %s" % (
                    current_iter_steps, self.best
                ))
            current_iter_steps += 1
        return self.best

    def _spawn_particles(self):
        for _i in range(self.no_particles):
            particle = Particle(
                self.optimization_object, self.learning_factors
            )
            self.particles.append(particle)
            if is_better(self.best[0], particle.value,
                         self.find_max):
                self.best = (particle.value, deepcopy(particle.position))

        try:
            self.snapshots.append(
                tuple([deepcopy(self.particles), deepcopy(self.best)])
            )
        except AttributeError:
            pass

    def _pso_do_iter(self):
        """For each iteration step, solve() function will make a call to this
        function."""
        for particle in self.particles:
            particle.update(self.best)
            if is_better(self.best[0], particle.value,
                         self.find_max):
                self.best = (particle.value, deepcopy(particle.position))

        try:
            self.snapshots.append(
                tuple([deepcopy(self.particles), deepcopy(self.best)])
            )
        except AttributeError:
            pass
