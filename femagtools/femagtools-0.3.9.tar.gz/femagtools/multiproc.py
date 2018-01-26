"""
    femagtools.engine.multiproc
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Creating and managing multicore/multiprocessing jobs



    :authors: R. Tanner, N. Mauchle
"""
import sys
import multiprocessing
import subprocess
import os
import logging
from .job import Job
import femagtools.config as cfg
try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

logger = logging.getLogger(__name__)


def run_femag(cmd, workdir, fslfile):
    """Start the femag command as subprocess.

    :internal:

    Args:
        cmd: The program (executable image) to be run
        workdir: The workdir where the calculation files are stored
        fslfile: The name of the start file (usually femag.fsl)
    """
    logger.info('FEMAG %s: %s', workdir, fslfile)
    with open(os.path.join(workdir, "femag.out"), "wb") as out, \
            open(os.path.join(workdir, "femag.err"), "wb") as err:
        try:
            proc = subprocess.Popen(cmd + ['-b', fslfile],
                                    shell=False,
                                    stdin=DEVNULL,
                                    stdout=out,
                                    stderr=err,
                                    cwd=workdir)
        except OSError:
            logger.error("Command {} not found in path".format(cmd))
            raise

        # wait
        proc.wait()

    logger.info("Finished pid: %d return %d", proc.pid, proc.returncode)
    return proc.returncode


class Engine:
    """The MultiProc engine uses a pool of local calculation processes.

    This is more or less a decorator for the `Python multiprocessing Module
    <https://docs.python.org/3.6/library/multiprocessing.html>`_

    Args:
        cmd: the program (executable image) to be run 
            (femag dc is used if None)
        process_count: number of processes (cpu_count() if None)
    """
    def __init__(self, cmd=None, process_count=None):
        self.process_count = process_count
        if cmd:
            self.cmd = [cmd]
        else:
            self.cmd = [cfg.get_femag()]
            if not sys.platform.startswith('linux'):
                    self.cmd.append('-m')

    def create_job(self, workdir):
        """Create a FEMAG :py:class:`Job`

        Args:
            workdir: The workdir where the calculation files are stored
        
        Return:
            FEMAG :py:class:`Job`
        """
        self.job = Job(workdir)
        return self.job

    def submit(self):
        """Starts the FEMAG calculation(s) with the internal
        :py:meth:`multiproc.run_femag` function

        Return:
            length of started tasks
        """
        pool = multiprocessing.Pool(self.process_count)
        self.tasks = [pool.apply_async(run_femag,
                                       args=(self.cmd,
                                             t.directory,
                                             t.fsl_file))
                      for t in self.job.tasks]
        pool.close()  # used to free resources after calculations have finished. thomas.maier/OSWALD
        return len(self.tasks)

    def join(self):
        """Wait until all calculations are finished

        Return:
            list of all calculations status (C = Ok, X = error)
        """
        results = [task.get() for task in self.tasks]
        status = []
        for t, r in zip(self.job.tasks, results):
            t.status = 'C' if r == 0 else 'X'
            status.append(t.status)

        return status
