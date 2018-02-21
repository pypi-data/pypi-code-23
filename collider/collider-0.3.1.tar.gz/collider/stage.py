# -*- author: Dimitri Scheftelowitsch -*-
# -*- coding:utf-8 -*-
import logging
import os

import errno

import time
from threading import Timer

from typing import Any, Dict, Iterable, Mapping, Tuple
from subprocess import check_output, Popen, PIPE
from hashlib import sha256


def eintr_retry_call(func, *args):
    while True:
        try:
            return func(*args)
        except InterruptedError:
            continue


class ResourcePopen(Popen):
    def _try_wait(self, wait_flags):
        """All callers to this function MUST hold self._waitpid_lock."""
        try:
            (pid, sts, res) = eintr_retry_call(os.wait4, self.pid, wait_flags)
        except OSError as e:
            if e.errno != errno.ECHILD:
                raise
            # This happens if SIGCLD is set to be ignored or waiting
            # for child processes has otherwise been disabled for our
            # process.  This child is dead, we can't get the status.
            pid = self.pid
            sts = 0
        else:
            self.rusage = res
        return (pid, sts)


def resource_call(*popenargs, timeout=None, **kwargs):
    """Run command with arguments.  Wait for command to complete or
    timeout, then return the returncode attribute and resource usage.

    The arguments are the same as for the Popen constructor.  Example:

    retcode, rusage = call(["ls", "-l"])
    """
    log = logging.getLogger("collider")
    kwargs['stdout'] = PIPE
    killed = False

    def kill_process(process: Popen):
        nonlocal killed
        log.info("Kill process {0}".format(process))
        killed = True
        process.kill()

    with ResourcePopen(*popenargs, **kwargs) as p:
        timer = None
        if timeout is not None:
            timer = Timer(timeout, lambda process: kill_process(process), [p])
        try:
            if timeout is not None:
                timer.start()
            out = p.stdout.read()
            retcode = p.wait(timeout=timeout)
            if timeout is not None:
                timer.cancel()

            return retcode, p.rusage, out, killed
        except:
            p.kill()
            p.wait()
            raise
        finally:
            if timeout is not None:
                timer.cancel()


class Stage:
    def __init__(self, name):
        self.name = name

    def execute(self, value: Any, stats: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("This is a pure virtual method!")


class ExecutableStage(Stage):
    def __init__(self, experiment_name: str, exe: str, args: Iterable, patterns: Iterable[str], timeout=600,
                 save_output=True):
        Stage.__init__(self, exe)
        self.exe = exe
        self.args = args
        self.patterns = patterns
        self.stats = {}
        self.experiment_name = experiment_name
        self.timeout = timeout
        self.save_output = save_output

    def filename(self, stage: str, value: Any) -> Tuple[str, str]:
        dir_pattern = "{0}_intermediate/{1}"
        file_pattern = "{0}/{1}"
        hashed = "_".join([str(v) for v in value])
        hashed_value = sha256(repr(value).encode('utf-8')).hexdigest()
        directory = dir_pattern.format(self.experiment_name, hashed)
        return directory, file_pattern.format(directory, stage)

    def output(self, value: Mapping[int, Any], stats: Dict[str, Any]) -> bytes:
        log = logging.getLogger("collider")
        value_dict = {}
        for i, k in enumerate(self.args):
            value_dict[k] = value[i]
        for i, stage in enumerate(stats.keys()):
            value_dict[stage] = stage
        cmdline = [p.format(**value_dict) for p in self.patterns]
        # log.debug(cmdline)
        cmdline = [self.exe] + cmdline
        log.debug("command line: {}".format(cmdline))
        directory, _ = self.filename(self.name, value)

        try:
            retcode, rusage, stdout, killed = resource_call(cmdline, close_fds=True, timeout=self.timeout,
                                                            cwd=directory)
            # log.info("stderr output: {}".format(stderr))
            # save the output of the program only if we wish so (which is more often than not not the case)
            if self.save_output:
                self.stats['output'] = stdout

            self.stats['cpu_user'] = rusage.ru_utime
            self.stats['cpu_system'] = rusage.ru_stime
            self.stats['timeout'] = killed
            return stdout
        except Exception as e:
            log.error(e)
            self.stats['output'] = ""
            self.stats['cpu_user'] = self.timeout
            self.stats['cpu_system'] = 0.0
            self.stats['timeout'] = True
            return b""

    def execute(self, value: Mapping[int, Any], stats: Dict[str, Any]) -> Dict[str, bytes]:
        self.output(value, stats)
        return self.stats


class ExecutableFileOutputStage(ExecutableStage):
    def __init__(self, experiment_name: str, exe: str, args: Iterable, patterns: Iterable[str], timeout=None,
                 save_output=True):
        ExecutableStage.__init__(self, experiment_name, exe, args, patterns, timeout=timeout, save_output=save_output)

    def execute(self, value: Mapping[int, Any], stats: Dict[str, Any]):
        # create directory for intermediate results
        directory, file = self.filename(self.name, value)
        if not os.path.exists(directory):
            os.mkdir(directory)
        # run
        output = self.output(value, stats)
        f = open(file=file, mode='w+b')
        f.write(output)
        f.close()
        return self.stats
