import shlex
import subprocess

import psutil

from lib import logger


class ExecutableProcess(object):
    """
    A Wrapper for process information (via psutil) and execution (via subprocess.Popen)
    """

    class ExecutableProcessError(Exception):
        pass

    def __init__(self, args, popen_kwargs=None):
        if args[0] == "start":
            self._check_args = args[1:]
        else:
            self._check_args = args
        # Popen values
        self._args = args
        self._kwargs = popen_kwargs or {}
        # The Popen object opened at execution
        self._popen_process = None
        self._process = None
        self.match_running()

    @classmethod
    def from_pid(cls, pid):
        """
        Create an ExecutableProcess from a given process id
        :param pid: the sought process id as int
        :return: ExecutableProcess or None on failure
        """
        if psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            return cls(proc.cmdline(), popen_kwargs={'executable': proc.exe(), 'cwd': proc.cwd()})
        return None

    @classmethod
    def from_cmdline(cls, cmdline):
        """
        Create an ExecutableProcess from a given cmdline
        :param cmdline: the command line of the sought process as a string
        :return: ExecutableProcess or None on failure
        """
        encountered_access_denied = False
        cmdlist = cmdline.split(" ")
        for proc in psutil.process_iter():
            try:
                if proc.cmdline() == cmdlist:
                    return cls(proc.cmdline(), popen_kwargs={'executable': proc.exe(), 'cwd': proc.cwd()})
            except psutil.AccessDenied:
                encountered_access_denied = True
                # ignore processes we can't access
                continue
        if encountered_access_denied:
            # This warning doesn't mean that there's a problem; only that the WatchDog is running not as root/admin
            logger.logger.warning("%s.from_cmdline didn't find a process with cmdline:'%s'."
                                  "We might have missed the process due to AccessDenied errors" % (
                                      cls.__name__, cmdline))
        return None


    @classmethod
    def from_exec(cls, executable):
        """
        Create an ExecutableProcess from a given cmdline
        :param executable: the path to the program being run
        :return: ExecutableProcess or None on failure
        """
        encountered_access_denied = False
        for proc in psutil.process_iter():
            try:
                if proc.exe() == executable:
                    return cls(proc.cmdline(), popen_kwargs={'executable': proc.exe(), 'cwd': proc.cwd()})
            except psutil.AccessDenied:
                encountered_access_denied = True
                # ignore processes we can't access
                continue
        if encountered_access_denied:
            # This warning doesn't mean that there's a problem; only that the WatchDog is running not as root/admin
            logger.logger.warning("%s.from_cmdline didn't find a process with executable:'%s'."
                                  "We might have missed the process due to AccessDenied errors" % (
                                      cls.__name__, executable))
        return None


    @property
    def popen(self):
        return self._popen_process

    @property
    def info(self):
        return self._process

    def match_running(self):
        """
        Find a process object (representing a live process) matching our execution details
        :return a psutil.Process matching the execution args / kwargs provided, or None if not found.
        """
        # If we have a process object (Popen) we opened, check if it's still running
        if self._popen_process is not None and isinstance(self._process, psutil.Process):
            if self._process.is_running():
                return self._process
        # If we didn't open a process, or couldn't find our process running
        # Check if we can find a new matching process by execution details
        for process in psutil.process_iter():
            try:
                # if this process matches our execution details
                if process.cmdline() == self._check_args:
                    executable = self._kwargs["executable"]
                    if executable is not None and executable == process.exe():
                        self._process = process
                        return process
                    elif executable is None:
                        self._process = process
                        return process
            except Exception:
                continue
        # If we couldn't match a process, return None
        return None

    def suspend(self):
        assert isinstance(self._process, psutil.Process)
        self._process.suspend()

    def resume(self):
        assert isinstance(self._process, psutil.Process)
        self._process.resume()

    def kill(self):
        assert isinstance(self._process, psutil.Process)
        self._process.kill()

    def assure_running(self):
        """
        Check if a process like ours is running, if not start it
        """
        running = self.match_running()
        if running is None:
            self.execute()
        if not self.match_running():
            raise RuntimeError("Failed to start process %s" % self.info)

    def execute(self):
        """
        Start the process we are configured to, and update process info internally.
        """
        self._popen_process = subprocess.Popen(self._args, **self._kwargs)
        self._process = psutil.Process(self._popen_process.pid)

    @classmethod
    def start_process(cls, cmdline, executable=None, cwd=None,
                      shell=False,
                      execute_once=True, wait=False,
                      expect_code=0, expect_stdout=None, expect_stderr=""):
        """
        Start a sub-process
        :param [str,list] cmdline: command line to start the process
        :param str executable: optional executable path to be passed Popen
        :param str cwd: optional current working directory path to be passed to Popen
        :param bool shell: if True the cmdline will be passed to the shell
        :param bool execute_once: if True the process will not be executed if an equal one is already up
        :param bool wait: Should the call wait for the process to exit (uses Popen.communicate)
                          Enables usage of the expect_* arguments
        :param str expect_stderr: Used with wait=True, checks the resulting stderr
                                    and raises ExecutableProcessError if it differs from the passed value
        :param str expect_stdout: Used with wait=True, checks the resulting stdout
                                    and raises ExecutableProcessError if it differs from the passed value
        :param int expect_code: Used with wait=True, checks the resulting return-code
                                    and raises ExecutableProcessError if it differs from the passed value
        :returns: the ExecutableProcess of the started process
        """
        if isinstance(cmdline, list):
            args = cmdline
        else:
            args = shlex.split(cmdline)
        proc = cls(args=args, popen_kwargs={'executable': executable, 'cwd': cwd,
                                            'shell': shell,
                                            # Channel pipes so the process won't hang
                                            "stdin": subprocess.PIPE,
                                            "stdout": subprocess.PIPE,
                                            "stderr": subprocess.PIPE})
        if execute_once:
            proc.assure_running()
        else:
            proc.execute()
        if wait:
            stdout, stderr = proc.popen.communicate()
            if expect_code and expect_code != proc.popen.returncode:
                raise cls.ExecutableProcessError(
                    "Expected return-code %d for command '%s', got %d"
                    % (expect_code, cmdline, proc.popen.returncode))
            if expect_stderr and expect_stderr != stderr:
                raise cls.ExecutableProcessError(
                    "Expected stderr '%s' for command '%s', got '%s'"
                    % (expect_stderr, cmdline, stderr))
            if expect_stdout and expect_stdout != stdout:
                raise cls.ExecutableProcessError(
                    "Expected stdout '%s' for command '%s', got '%s'"
                    % (expect_stdout, cmdline, stdout))
        return proc

    @classmethod
    def run_shell(cls, cmdline, cwd=None, wait=False,
                  expect_code=0, expect_stdout=None, expect_stderr=""):
        """
        Convenience wrapper for start_process to run commands through the shell
        """
        proc = cls.start_process(cmdline, cwd=cwd, wait=wait, shell=True, execute_once=False,
                                 expect_code=expect_code, expect_stdout=expect_stdout,
                                 expect_stderr=expect_stderr)
        return proc
