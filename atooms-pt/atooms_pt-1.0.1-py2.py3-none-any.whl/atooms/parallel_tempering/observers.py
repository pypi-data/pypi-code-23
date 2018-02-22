"""Writer callbacks specific to parallel tempering."""

import numpy
from atooms.core.utils import rank, size, comm


def write_config(sim, include=None):
    """
    Write configurations from parallel tempering instance `sim` to disk

    `include` is a list of replicas for which configuations will be
    written. If `include` is `None`, configurations are written for
    all replicas.
    """
    for i in sim.my_replica:
        irx = sim.state[i]
        if include is None or irx in include:
            # We need two things here: a trajectory class that is
            # appropriate to the backend (actually, any trajectory
            # would be fine as long as the backend implements System
            # interface) and an output file (or output directory).
            #
            # The trajectory class is taken from the simulation backend
            trj_cls = sim.sim[irx].trajectory
            with trj_cls(sim.output_path_state[irx], 'a') as t:
                try:
                    t.exclude(['velocity'])
                except AttributeError:
                    pass
                t.write(sim.replica[i], sim.current_step)


def write_thermo(sim):
    """Write thermodynamic properties of parallel tempering instance `sim`"""
    # Since we grab steps from simulations, we must gather them first.
    # We could have each process write down its replicas and make it
    # more efficient, this used to be self.write_state()
    #
    # TODO: write state atomically, avoid parallelization and remove communications
    u = numpy.ndarray(sim.number_replicas)
    k = numpy.ndarray(sim.number_replicas)
    u_l = numpy.ndarray(len(sim.my_replica))
    k_l = numpy.ndarray(len(sim.my_replica))
    rmsd = numpy.ndarray(sim.number_replicas)
    rmsd_l = numpy.ndarray(len(sim.my_replica))
    steps = numpy.ndarray(sim.number_replicas, dtype=int)
    steps_l = numpy.ndarray(len(sim.my_replica), dtype=int)
    for i, ri in enumerate(sim.my_replica):
        u_l[i] = sim.replica[ri].potential_energy()
        k_l[i] = sim.replica[ri].kinetic_energy()
        rmsd_l[i] = sim.sim[ri].rmsd
        steps_l[i] = sim.sim[ri].current_step

    if size > 1:
        comm.Gather(u_l, u, 0)
        comm.Gather(k_l, k, 0)
        comm.Gather(rmsd_l, rmsd, 0)
        comm.Gather(steps_l, steps, 0)
    else:
        u = u_l
        k = k_l
        rmsd = rmsd_l
        steps = steps_l

    if rank == 0:
        # Loop over replicas
        for i in range(sim.number_replicas):
            f = sim.output_path + '/replica/%d.out' % i
            if sim.current_step == 0:
                with open(f, 'w') as fh:
                    fh.write('# columns: ' + ', '.join(['steps',
                                                        'backend steps',
                                                        'state id',
                                                        'rmsd',
                                                        ]) + '\n')
            with open(f, 'a') as fh:
                # In which state is physical replica i ?
                fh.write('%d %d %d %g\n' % (sim.current_step,
                                            steps[i], sim.state[i], rmsd[i]))

        # Loop over states
        for i in range(sim.number_replicas):
            # Output file per state
            f = sim.output_path + '/state/%d.out' % i
            if sim.current_step == 0:
                with open(f, 'w') as fh:
                    fh.write('# columns: ' + ', '.join(['steps',
                                                        'backend steps',
                                                        'replica id',
                                                        'potential energy',
                                                        'kinetic energy'
                                                        ]) + '\n')
            with open(f, 'a') as fh:
                # Which replica is in state i? What is its energy?
                irep = sim.replica_id[i]
                fh.write('%d %d %d %.6g %.6g\n' % (sim.current_step,
                                                   steps[i], irep,
                                                   u[irep], k[irep]))

            # Thermo output file
            f = sim.output_path_state[i] + '.thermo'
            if sim.current_step == 0:
                with open(f, 'w') as fh:
                    fh.write('# columns: ' + ', '.join(['steps',
                                                        'backend steps',
                                                        'potential energy per particle',
                                                        'kinetic energy per particle'
                                                        ]) + '\n')
            with open(f, 'a') as fh:
                # Which replica is in state i? What is its energy?
                irep = sim.replica_id[i]
                npart = max(1, len(sim.replica[irep].particle))
                fh.write('%d %d %g %g\n' % (sim.current_step, steps[i],
                                            u[irep] / npart, k[irep] / npart))
