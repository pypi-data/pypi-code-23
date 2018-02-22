# This file is part of atooms
# Copyright 2010-2014, Daniele Coslovich

"""
Parallel tempering simulation.

In a parallel tempering simulation, replicas of the system of interest
are evolved in time by corresponfing simulation instances. At regular
intervals during the simulation, attempts are made to exchange the
states of selected pairs of replicas. Note we do not exchange
configurations, but simulation states (replica-centric approach). Each
step of a parallel tempering simulation comprises several steps of the
underlying simulation instances.

In parallel, replicas are distributed evenly to processes. We lazily
keep copies of "unused" physical replica in each process. The relevant
replicas are identified using the `my_replica` list. This list is
updated after each exchange.

Trajectories are defined internally by Simulation instances. The
actual backend might be changed by the user at run time. It's not the
responsability of parallel tempering to handle the trajectory backend.
Each simulation handles its own trajectory backend.
"""

import os
import random
import numpy
import datetime
import logging
import time

from atooms.simulation import Simulation
from atooms.backends.dryrun import DryRun
from atooms.core.utils import rank, size, comm, barrier
from atooms.core.utils import rmd, rmf, mkdir

from atooms.parallel_tempering import nvt
from ._version import __version__ as __bare_version
try:
    from ._commit import __commit__, __date__
    __version__ = '%s+%s (%s)' % (__bare_version, __commit__, __date__)
except ImportError:
    __commit__ = ""
    __date__ = ""
    __version__ = __bare_version

_log = logging.getLogger(__name__)


class ParallelTempering(Simulation):

    version = __version__

    def __init__(self, sim, params, output_path, seed=10, steps=None,
                 checkpoint_interval=0, restart=False, exchange=nvt,
                 exchange_interval=0, exchange_scheme='alternate',
                 exchange_parameters=None, exchange_fmt=None):
        # TODO: we should not need to pass a dryrun backend
        Simulation.__init__(self, DryRun(), output_path=output_path,
                            steps=steps, checkpoint_interval=checkpoint_interval,
                            restart=restart)
        self.sim = sim
        """A list of simulation instances"""
        self.seed = seed
        """Seed for the random number generator"""
        self.params = params
        """List of parameter values."""
        self.exchange = exchange
        """Exchange backend module. It defaults to temperature exchanges."""
        self.exchange_interval = exchange_interval
        """Interval in backend steps between exchanges"""
        self.exchange_scheme = exchange_scheme
        """String describing the exchange scheme"""
        # We can overwrite the parameters and formatting string in the
        # exchange backend module
        if exchange_parameters is not None:
            self.exchange.parameters = exchange_parameters
        if exchange_fmt is not None:
            self.exchange.fmt = exchange_fmt

        # Sanity checks
        if len(params) != len(sim):
            raise ValueError('n. backends must match n. states (%d, %d)' % (len(params), len(sim)))
        for s in self.sim:
            if s.output_path is not None:
                _log.warn('output path %s in backend will be overwritten', s.output_path)
                break

        # Initialize internal state
        random.seed(self.seed)
        self.number_replicas = len(params)
        """Number of replicas"""
        self.state = range(self.number_replicas)
        """List of the states in replica order"""
        self.replica_id = range(self.number_replicas)
        """List of the replica id's in state order"""
        # TODO: remember to checkpoint them
        self.attempts = [0.0 for i in range(self.number_replicas)]
        """Exchange attempts"""
        self.accepted_attempts = [0.0 for i in range(self.number_replicas)]
        """Accepted exchange attempts"""
        # This is used to exchange odd/even replicas in turn
        self._offset = 0

        # Listify exchange interval (one per replica)
        if not type(exchange_interval) is list:
            self.exchange_interval = [exchange_interval] * self.number_replicas

        # Get physical replicas (systems) from simulation instances.
        # These are references: they'll follow the simulations
        self.replica = [s.system for s in sim]
        self.system = self.replica[0]

        # This will be set as output_path of the backend in a moment
        self.output_path_state = []
        if hasattr(self.exchange, 'fmt'):
            for p in self.params:
                fmt = '%s/state/' + self.exchange.fmt + '/trajectory'
                dir_path = fmt % (self.output_path, p)
                self.output_path_state.append(dir_path)
        else:
            for i in range(self.number_replicas):
                dir_path = '%s/state/%d/trajectory' % (self.output_path, i)
                self.output_path_state.append(dir_path)

        # Distribute physical replicas in parallel.
        # Each process gets a bunch of replicas to evolve
        # replica_id contains their state id's.
        # We could as well distributes states, which would allow
        # for other optimizations.
        np = self.number_replicas / size
        ni = rank * np
        nf = (rank + 1) * np
        self.my_replica = range(ni, nf)
        """List of replicas associated to process `rank`"""
        self.process_with_replica = numpy.array(range(self.number_replicas))
        """For a given replica id, which process is associated to it"""
        for irank in range(size):
            ni = irank * np
            nf = (irank + 1) * np
            for nr in range(ni, nf):
                self.process_with_replica[nr] = irank
        barrier()

        # Output paths
        # If we do not restart, we clear up everything in the base
        if not self.restart:
            rmf(self.output_path + '/pt.log')
            rmd(self.output_path + '/state')
            rmd(self.output_path + '/replica')

        # Make sure base directories exist
        mkdir(self.output_path)
        mkdir(self.output_path + '/state')
        mkdir(self.output_path + '/replica')
        # Make sure output directories exist, even if we dont write config (for checkpoint)
        for d in self.output_path_state:
            mkdir(d)

        # Write parameters log file
        self._write_log()

    def __str__(self):
        return 'Parallel tempering'

    def _process_with(self, state):
        return self.process_with_replica[self.replica_id[state]]

    def acceptance(self, state):
        """Acceptance ratio for a given `state`"""
        if self.attempts[state] > 0:
            return self.accepted_attempts[state] / self.attempts[state]
        else:
            return 0.0

    @property
    def rmsd(self):
        """Minimum root mean square displacement among replicas"""
        # RMSD must be known on all processes, thus an allgather is needed
        # This might be optimized by targeting rmsd dynamically.
        rmsd_l = numpy.ndarray(len(self.my_replica))
        for i, ri in enumerate(self.my_replica):
            rmsd_l[i] = self.sim[ri].rmsd
        if size > 1:
            rmsd = numpy.ndarray(self.number_replicas)
            comm.Allgather(rmsd_l, rmsd)
            return min(rmsd)
        else:
            return min(rmsd_l)

    def _elapsed_wall_time(self):
        """Normalized elapsed wall time in seconds."""
        return (time.time() - self._start_time) / sum(self.exchange_interval)

    def _write_log(self):
        """ Dump state parameters """
        with open(self.output_path + '/pt.log', 'w') as fh:
            for i, param in enumerate(self.params):
                fh.write('%d %s\n' % (i, param))

    def write_checkpoint(self):
        """
        Checkpoint replicas via simulation backends as well as the
        thermodynamic states in which the replicas found themselves.
        """
        # TODO: Only if all check points (state, replica) have been written we can safely restart!
        #
        # We should therefore first keep the old checkpoints, create
        # new files and then move (which is quick).
        #
        # Additionally we should check consistency upon reading
        # (i.e. all checkpoints should belong to the same step) and
        # fail otherwise
        _log.debug('write checkpoint %d', self.current_step)
        # Note: offset and step are redundant, since they are global
        for i in self.my_replica:
            outfile = self.output_path + '/replica/%d.out.chk' % i
            with open(outfile, 'w') as fh:
                fh.write('%d\n' % self.state[i])
                fh.write('%d\n' % self.current_step)
                fh.write('%d\n' % self._offset)
            self.sim[i].write_checkpoint()

    def _check(self):
        """Consistency check"""
        for i, s in enumerate(self.state):
            if self.replica_id[s] != i:
                raise ValueError('replica ids do not match %d %d %d' %
                                 (i, s, self.replica_id[s]))

    def read_checkpoint(self):
        """Read checkpoint"""
        # TODO: steps should all be equal, we should check
        # This must be done by everybody. Otherwise, each process
        # should read its replicas and then gather.
        for i in range(self.number_replicas):
            f = self.output_path + '/replica/%d.out.chk' % i
            if os.path.exists(f):
                with open(f, 'r') as fh:
                    istate = int(fh.readline())
                    self.state[i] = istate
                    self.replica_id[istate] = i
                    self.current_step = int(fh.readline())
                    self._offset = int(fh.readline())
                _log.debug('pt restarting replica %d at state %d from step %d',
                           i, istate, self.current_step)
        _log.info('restarting from step %s', self.current_step)

        # Restarting is handled by the simulation instance. The
        # output directory for the checkpoint is controlled by the
        # simulation or backend instance.
        for i in self.my_replica:
            self.sim[i].read_checkpoint()

    def _info_backend(self):
        barrier()
        txt = 'backend: %s\n' % self.sim[0]
        txt += 'number of replicas: %d\n' % self.number_replicas
        txt += 'number of processes: %d\n' % size
        if self.exchange_interval[0] == self.exchange_interval[-1]:
            txt += 'exchange interval: %d\n' % self.exchange_interval[0]
        txt += 'process %s replicas: %s\n' % (rank, self.my_replica)
        txt += 'process %s states: %s' % (rank, [self.state[i] for i
                                                 in self.my_replica])
        return txt

    def _info_end(self):
        txt = '\n'
        txt += 'simulation ended on: %s\n' % datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')
        txt += 'final steps: %d\n' % self.current_step
        txt += 'final minimum rmsd: %.2f\n' % self.rmsd
        txt += 'wall time [s]: %.1f\n' % self.wall_time()
        txt += 'average TSP [s/step/replica]: %.2e\n' % self.wall_time(per_step=True)
        return txt

    def run_until(self, nsteps):
        """
        Run until the parallel tempering simulation has reached `nsteps`.

        One step of a parallel tempering simulation consists of a
        sweep of state exchange attempts through the replicas. Between
        two parallel tempering steps, the backends evolve the replicas
        for `exchange_interval` steps.
        """
        # Evolve my physical replicas.
        _log.debug('run until %d', nsteps)
        for i in self.my_replica:
            # This will evolve physical replica[i] for the number of
            # steps between exchanges prescribed for its state times the
            # number of steps.
            n = nsteps * self.exchange_interval[self.state[i]]
            _log.debug('evolve replica %d on rank %d for %d until %d',
                       i, rank, nsteps, n, extra={'rank': 'all'})
            self.sim[i].run_until(n)
        # Its up to us to update our steps
        self.current_step = nsteps

        # Attempt to exchange replicas.
        _log.debug("exchange rx")
        if self.exchange_scheme == 'alternate':
            self._alternate()
        self._check()

    def _alternate(self):
        for state in range(self._offset, self.number_replicas - 1, 2):
            # Index of physical replicas having states to exchange
            # Get process that has my nearest neighboring state
            sending = False
            if self.replica_id[state] in self.my_replica:
                this_state, other_state, sending = state, state + 1, True
            else:
                if self.replica_id[state + 1] in self.my_replica:
                    this_state, other_state, sending = state + 1, state, True
            if not sending:
                continue

            ri = self.replica_id[this_state]
            rj = self.replica_id[other_state]
            other_process = self._process_with(other_state)
            # Check if we accept the exchange between replicas ri and rj
            x = self.exchange.accept(self.replica, ri, rj, other_process)
            _log.debug('rank %d accepted %s states %d, %d', rank, x, this_state, other_state)
            if x:
                ri = self.state.index(this_state)
                rj = self.state.index(other_state)
                self.state[ri], self.state[rj] = self.state[rj], self.state[ri]
        barrier()

        # Sync states in parallel
        if size > 1:
            tmp = comm.allgather([self.state[i] for i in self.my_replica])
            # Flatten list of lists
            # see http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
            self.state = sum(tmp, [])

        # Global update state of replica ids and simulation objects
        for i, s in enumerate(self.state):
            self.replica_id[s] = i
            self.exchange.update(self.sim[i], self.params[s])

        # Update offset
        self._offset = (self._offset + 1) % 2
