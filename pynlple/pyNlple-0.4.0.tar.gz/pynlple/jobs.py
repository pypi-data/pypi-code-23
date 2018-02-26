# -*- coding: utf-8 -*-
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic
from IPython.lib.backgroundjobs import BackgroundJobManager
from IPython import get_ipython
import time


@magics_class
class ThreadedJobsMagics(Magics):

    def __init__(self, shell_):
        self.jobs = BackgroundJobManager()
        super(ThreadedJobsMagics, self).__init__(shell_)

    @line_cell_magic
    def job(self, line, cell=None):
        """Run a job in new thread. May be run in cell or line fashion."""
        return self.jobs.new(cell if cell else line, self.shell.user_global_ns)

    @line_magic
    def manager(self, line=None):
        """Get a jobs manager."""
        return self.jobs

    @line_magic
    def try_kill_job(self, line):
        """Attemp to stop a job by killing the job's thread.
        Provide with a job thread object only in the line expression.
        Uses pynlple.jobs.try_kill_thread_job method."""
        thread = eval(line)
        return try_kill_thread_job(thread)


shell = get_ipython()

threaded_jobs_magics = ThreadedJobsMagics(shell)
shell.register_magics(threaded_jobs_magics)


def try_kill_thread_job(thread):
    """
    Attempts to kill a thread in which a certain job was run. Does not assures the job is stopped.
    Uses ctypes.pythonapy.PyThreadState_SetAsyncExc to inject SystemError in a process running.

    :param threading.Thread thread: thread that contains a job to stop.
    :raises ValueError: if ctypes.pythonapy.PyThreadState_SetAsyncExc failed when thread process was not found.
    :raises SystemError: if ctypes.pythonapy.PyThreadState_SetAsyncExc failed while nulling (zeroing) thread process id.
    """
    import ctypes

    id = thread.ident
    code = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(id),
        ctypes.py_object(SystemError)
    )
    if code == 0:
        raise ValueError('invalid thread id')
    elif code != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(id),
            ctypes.c_long(0)
        )
        raise SystemError('PyThreadState_SetAsyncExc failed')


def load_ipython_extension(ipython):
    threaded_jobs_magics = ThreadedJobsMagics(ipython)
    ipython.register_magics(threaded_jobs_magics)


def unload_ipython_extension(ipython):
    pass
