import unittest
import numpy as np
from ..tise import get_initial_state

class TestTISE(unittest.TestCase):

    def test_particle_in_a_box(self):
        """Test particle in a box"""
        def potential(x):
            return np.zeros_like(x)

        dx = 0.01
        grid = np.arange(dx,5, dx)

        psi0, _ = get_initial_state(grid, potential)

        # Test electron density as the ground-state solution with the same
        # Hamiltonian is unique only up to a global phase
        np.testing.assert_allclose(np.fabs(psi0)**2,
                                   np.fabs(np.sqrt(2/5)*np.sin(np.pi/5*grid))**2,
                                   rtol = 1e-5)

    def test_particle_in_harmonic_oscillator(self):
        """Test particle in a box"""
        def potential(x):
            return 0.5*x*x

        dx = 0.01
        grid = np.arange(-10,10, dx)

        psi0, _ = get_initial_state(grid, potential)

        np.testing.assert_allclose(np.fabs(psi0)**2,
                                   np.fabs(1.0/np.power(np.pi,0.25)*np.exp(-grid*grid/2))**2,
                                   atol = 1e-5)
