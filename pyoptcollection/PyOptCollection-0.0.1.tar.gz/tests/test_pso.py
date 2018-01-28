"""Test py_opt_collection.pso 's classes."""

from py_opt_collection.pso import \
    Particle, PSO
from py_opt_collection.test_functions import \
    HIMMELBLAU, ROSENBROCK


class TestParticle(object):
    """Tests for py_opt_collection.pso.Particle class."""

    def test___init__(self, fix_optimization_object):
        """Test the constructor function."""

        # Seed = 928371 to have the particle spawn again to have position
        # satisfy all the constraints.
        fix_optimization_object.random_generator.seed(928371)
        particle = Particle(fix_optimization_object, (2.0, 2.0))
        assert particle.learning_factors == (2.0, 2.0)
        assert isinstance(particle.position, list)
        assert isinstance(particle.velocity, list)
        assert particle.position.__len__() == \
            particle.velocity.__len__() == \
            fix_optimization_object.no_dimensions
        assert particle.value == particle.best[0]
        assert particle.position == particle.best[1]
        assert particle.optimization_object.check_constraints(
            particle.position
        )

    def test_update(self, fix_optimization_object):
        """
        Test Particle.update() function.
        Success cases:
        - Particle choosing new velocity and position without breaking the
        constraints. New position is not better than the local best.
        - Particle choosing new velocity and position without breaking the
        constraints. New position give better value than the local best.
        """

        # Have to regenerate velocity
        fix_optimization_object.random_generator.seed(918474)
        particle_1 = Particle(fix_optimization_object, (2.0, 2.0))
        particle_1.update(global_best=(0.5, [0.4]))
        assert particle_1.optimization_object.check_constraints(
            particle_1.position
        )

        # # Have better local value
        fix_optimization_object.random_generator.seed(645909)
        particle_3 = Particle(fix_optimization_object, (2.0, 2.0))
        particle_3.update(global_best=(0.5, [0.4]))
        assert particle_3.optimization_object.check_constraints(
            particle_3.position
        )


class TestPSO(object):
    """Tests for py_opt_collection.pso.PSO class."""

    def test___init__(self, fix_optimization_object):
        no_particles = 10
        no_iteration_steps = 20
        pso_1 = PSO(optimization_object=fix_optimization_object,
                    no_particles=no_particles,
                    no_iteration_steps=no_iteration_steps,
                    c_1=2.0,
                    c_2=2.0)
        assert pso_1.optimization_object == fix_optimization_object
        assert pso_1.no_particles == no_particles
        assert pso_1.no_iteration_steps == no_iteration_steps
        assert pso_1.learning_factors == (2.0, 2.0)
        assert isinstance(pso_1.particles, list)
        assert isinstance(pso_1.best, tuple)

    def test_solve(self, fix_optimization_object, capsys):
        pso_1 = PSO(optimization_object=fix_optimization_object,
                    no_particles=100,
                    no_iteration_steps=200,
                    c_1=2.0,
                    c_2=2.0)
        result = pso_1.solve()
        assert isinstance(result, tuple)
        assert result[0] <= -4.130395

        pso_2 = PSO(optimization_object=fix_optimization_object,
                    no_particles=10,
                    no_iteration_steps=20,
                    c_1=2.0,
                    c_2=2.0,
                    historical=True,
                    verbose=True)
        pso_2.solve()
        assert pso_2.snapshots.__len__() == 20
        out, err = capsys.readouterr()
        for i in range(20):
            assert out.find("Iteration step #%d" % i) > -1

    def test_himmelblau(self):
        pso = PSO(optimization_object=HIMMELBLAU['optimization'],
                  no_particles=140,
                  no_iteration_steps=225,
                  c_1=1.0520,
                  c_2=0.8791)
        pso.solve()
        at_least_matched = False
        for r in HIMMELBLAU['results']:
            matched = abs(r[0] - pso.best[0]) < 5e-5
            print(r[0] - pso.best[0])
            for i in range(len(r[1])):
                matched &= abs(r[1][i] - pso.best[1][i]) < 1e-2

            at_least_matched |= matched
        assert at_least_matched

    def test_rosenbrock(self):
        pso = PSO(optimization_object=ROSENBROCK['optimization'],
                  no_particles=100,
                  no_iteration_steps=230,
                  c_1=1.2215,
                  c_2=1.5416)
        pso.solve()
        at_least_matched = False
        for r in ROSENBROCK['results']:
            matched = abs(r[0] - pso.best[0]) < 5e-5
            print(r[0] - pso.best[0])
            for i in range(len(r[1])):
                matched &= abs(r[1][i] - pso.best[1][i]) < 1e-2

            at_least_matched |= matched
        assert at_least_matched
