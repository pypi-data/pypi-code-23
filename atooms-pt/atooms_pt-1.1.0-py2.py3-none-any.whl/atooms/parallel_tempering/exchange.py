"""Exchange states in various ensembles"""

import random
import math
from atooms.core.utils import rank, size, comm, barrier
from atooms.parallel_tempering import helpers


def nvt(replica, i, j, other_process=None, parameters=('temperature', )):
    """
    Decide whether to accept an exchange in the NVT ensemble

    Return `True` if the exchange of states between replicas i and j
    can be accepted, according to detailed balance condition.
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


def npt(replica, i, j, other_process=None, parameters=('pressure', )):
    """
    Decide whether to accept an exchange in the NVT ensemble

    Return `True` if the exchange of states between replicas i and j
    can be accepted, according to detailed balance condition.
    """
    if 'temperature' in parameters:
        raise ValueError('cannot exchange T in npt yet')
    if other_process is None or other_process == rank:
        # Serial version
        # Get temperatures and energies of replicas
        T = replica[i].thermostat.temperature
        P_i = replica[i].barostat.pressure
        P_j = replica[j].barostat.pressure
        V_i = replica[i].cell.volume
        V_j = replica[j].cell.volume
        ran = random.random()
    else:
        # Parallel version
        # Get temperatures and energies of replicas
        T = replica[i].thermostat.temperature
        P_i = replica[i].barostat.pressure
        V_i = replica[i].cell.volume
        P_j = helpers.exchange(P_i, other_process)
        V_j = helpers.exchange(V_i, other_process)
        # Both rank and other_process should have the same random number
        # sync() ensures ran is is the same on both processes.
        ran = helpers.sync(random.random(), other_process)

    # Tell whether swap is accepted and store probability term
    x = math.exp((V_j - V_i) * (P_j - P_i) / T)
    return ran < x
