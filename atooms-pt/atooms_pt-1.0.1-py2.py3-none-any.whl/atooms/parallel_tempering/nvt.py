"""Exchange states in the NVT ensemble"""

import random
import math
from atooms.core.utils import rank, size, comm, barrier
from atooms.parallel_tempering import helpers

fmt = 'T%.4f'
"""A formatting string for the parameter values"""
parameters = ('temperature', )
"""A tuple with names of parameters to exchange"""


def update(simulation, *params):
    """Update the state of a simulation after an exchange."""
    # Note that when swapping certan thermostats, the internal
    # state should be reset.  It is OK for RUMD to only set the
    # temperatures from the params list
    simulation.system.thermostat.temperature = params[0]
    # We can test whether a parameter is in parameters to update
    # that parameter too. For instance:
    # if 'timestep' in parameters:
    # simulation.timestep = params[parameters.index('timestep')]


def accept(replica, i, j, other_process=None):
    """
    Return `True` if the exchange of states between replicas i and j
    satisfies detailed balance and should be accepted.
    """
    if other_process is None or other_process == rank:
        # Serial version
        # Get temperatures and energies of replicas
        T_i = replica[i].thermostat.temperature
        T_j = replica[j].thermostat.temperature
        u_i = replica[i].potential_energy()
        u_j = replica[j].potential_energy()
        ran = random.random()
    else:
        # Parallel version
        # Get temperatures and energies of replicas
        T_i = replica[i].thermostat.temperature
        T_j = replica[j].thermostat.temperature
        u_i = replica[i].potential_energy()
        u_j = helpers.exchange(u_i, other_process)
        # Both rank and other_process should have the same random number
        # sync() ensures ran is is the same on both processes.
        ran = helpers.sync(random.random(), other_process)

    # Tell whether swap is accepted and store probability term
    x = math.exp(-(u_j - u_i) * (1 / T_i - 1 / T_j))
    return ran < x
