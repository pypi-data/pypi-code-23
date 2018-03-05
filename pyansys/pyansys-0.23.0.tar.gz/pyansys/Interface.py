import os
import subprocess
import time


def Run(inputfile, jobname='file', nproc=4, outname='output.txt', memory=0,
        batch=False, rundir='', print_input=False, cleanup=False):
    """ Runs ANSYS """

    if not rundir:
        rundir = os.getcwd()

    inputfile = os.path.join(rundir, inputfile)

    # Check if input file exists
    if not os.path.isfile(inputfile):
        raise Exception('Input file %s does not exist' % inputfile)

    if os.path.isfile(os.path.join(rundir, jobname + '.lock')):
        print(os.path.join(rundir, jobname + '.lock'))
        raise Exception('Lock file exists for jobname ' + jobname)

    # add options
    options = ''
    options += '-j {:s} '.format(jobname)
    options += '-np {:d} '.format(nproc)
    options += '-o {:s} '.format(outname)
    options += '-i "{:s}" '.format(inputfile)
    if batch:
        options += '-b '

    if memory:
        options += '-m {:d} '.format(memory)

    command = "/usr/ansys_inc/v150/ansys/bin/ansys150 {:s}".format(options)
    if print_input:
        print(command)
    # subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    subprocess.Popen([command], stdout=subprocess.PIPE, shell=True, cwd=rundir)

    # wait until the lock is gone
    time.sleep(1)
    lockfile = os.path.join(rundir, jobname + '.lock')
    while os.path.isfile(lockfile):
        time.sleep(0.1)

    cleanup_ext = ['stat', 'mntr', 'log', 'full', 'esav', 'err', 'BCS']
    if cleanup:
        for ext in cleanup_ext:
            removefile = os.path.join(rundir, '%s.%s' % (jobname, ext))
            if os.path.isfile(removefile):
                os.remove(removefile)
