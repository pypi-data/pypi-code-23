#!python

"""Parallel tempering simulation driver"""

from atooms.core.utils import setup_logging
from atooms.core.utils import size, rank, barrier
from atooms.backends.rumd import RUMD
from atooms.simulation import Simulation, Scheduler
from atooms.parallel_tempering import ParallelTempering
from atooms.parallel_tempering.observers import write_thermo, write_config


def main(params):
    # TODO: dump params to a file in output_dir
    params.T = [float(_) for _  in params.T.split(',')]
    if params.forcefield is None:
        params.forcefield = params.input_file + '.ff'
    # Create simulation and integrators.
    # In parallel, read input file one process at a time.
    # TODO: parse multiple input files.
    for i in range(size):
        if i == rank:
            sa = [Simulation(RUMD(params.input_file,
                                  params.forcefield,
                                  temperature=T,
                                  integrator='nvt',
                                  fixcm_interval=params.fixcm_interval,
                                  dt=params.dt,
                                  output_path=params.output_dir + '/replica/%s' % i)) for
                  i, T in enumerate(params.T)]
        barrier()
    pt = ParallelTempering(sa, params.T, params.output_dir,
                           exchange_interval=params.exchange_interval,
                           checkpoint_interval=params.config_interval,
                           steps=params.steps,
                           exchange_scheme=params.exchange_scheme,
                           restart=params.restart)
    pt.add(write_config, Scheduler(params.config_interval))
    pt.add(write_thermo, Scheduler(1))
    setup_logging('atooms', level=20)
    setup_logging('parallel_tempering', level=20)
    pt.run()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', dest='verbose', action='store_true', help='verbose output')
    parser.add_argument('-T', dest='T', help='comma separated temperatures')
    parser.add_argument('--dt', dest='dt', type=float, default=0.004, help='time step')
    parser.add_argument('--ff', dest='forcefield', help='force field')
    parser.add_argument('-e', '--exchange-interval', dest='exchange_interval', type=int, default=50000, help='exchange interval')
    parser.add_argument('--exchange-scheme', dest='exchange_scheme', default='alternate_all', help='exchange scheme')
    parser.add_argument('-c', '--config-interval', dest='config_interval', type=int, default=1, help='config interval (in units of exchange periods)')
    parser.add_argument('--fixcm-interval', dest='fixcm_interval', type=int, default=100, help='interval in steps between CM fixing)')
    parser.add_argument('-n', '--steps', dest='steps', type=int, default=None, help='number of steps (in units of exchange periods)')
    parser.add_argument('-i', dest='input_file', help='input_file')
    parser.add_argument('-r', dest='restart', action='store_true', help='restart')
    parser.add_argument(dest='output_dir', help='output directory')
    args = parser.parse_args()
    main(args)
