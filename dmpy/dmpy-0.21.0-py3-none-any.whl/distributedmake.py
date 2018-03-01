import argparse
import contextlib
import os
import signal
from enum import Enum
import shlex
import subprocess
from tempfile import TemporaryDirectory, mkdtemp, mkstemp
import attr
import logging

import shutil

from dmpy.objects.dm_rule import DMRule

logger = logging.getLogger(__name__)


class SchedulingEngine(Enum):
    none = 0
    slurm = 1


def add_dm_args_to_argparse_object(object):
    object.add_argument("-r", "--run", action="store_true")
    object.add_argument("-j", "--jobs", type=int, default=1)
    object.add_argument("-c", "--no-cleanup", action="store_true")
    object.add_argument("-t", "--touch", action="store_true")
    object.add_argument("-k", "--keep-going", action="store_true")
    object.add_argument("-B", "--always-make", action="store_true")
    object.add_argument("--scheduler", default=SchedulingEngine.none.name)
    object.add_argument("--scheduler-args", default=None)
    return object


def get_dm_arg_parser(description="dmpy powered analysis"):
    parser = argparse.ArgumentParser(description=description)
    parser = add_dm_args_to_argparse_object(parser)
    return parser


@attr.s(slots=True)
class DMBuilder(object):
    shell = attr.ib(default="/bin/bash")
    rules = attr.ib(attr.Factory(list))
    scheduler = attr.ib(default=SchedulingEngine.none)
    scheduler_args = attr.ib(default=attr.Factory(list))
    _targets = attr.ib(attr.Factory(set))

    def add(self, target, deps, cmds):
        if target is None:
            raise ValueError("target may not be None type")
        if target in self._targets:
            raise Exception("Tried to add target twice: {}".format(target))
        self._targets.add(target)
        self.rules.append(DMRule(target, deps, cmds))

    def write_to_filehandle(self, fh):
        fh.write("SHELL = {}\n".format(self.shell))
        for rule in self.rules:
            dirname = os.path.abspath(os.path.dirname(rule.target))

            fh.write("{}: {}\n".format(rule.target, ' '.join(rule.deps)))
            if self.scheduler == SchedulingEngine.slurm:
                cmd_prefix = ['srun', '--quit-on-interrupt', '--job-name', rule.name]
                cmd_prefix += self.scheduler_args
                cmd_prefix += ['bash', '-c']
                cmd_prefix = ' '.join(cmd_prefix)
                rule.recipe = [cmd_prefix + ' ' + shlex.quote(cmd) for cmd in rule.recipe]
            rule.recipe.insert(0, "@test -d {0} || mkdir -p {0}".format(dirname))
            for cmd in rule.recipe:
                cmd = cmd.replace("$", "$$")
                fh.write("\t{}\n".format(cmd))

        fh.write("all: {}\n".format(" ".join([r.target for r in self.rules])))
        fh.write(".DELETE_ON_ERROR:\n")
        fh.flush()


@attr.s(slots=True)
class DistributedMake(object):
    run = attr.ib(False)
    keep_going = attr.ib(False)
    jobs = attr.ib(1)
    no_cleanup = attr.ib(False)
    question = attr.ib(False)
    touch = attr.ib(False)
    debug = attr.ib(False)
    always_make = attr.ib(False)
    shell = attr.ib('/bin/bash')
    exit_on_keyboard_interrupt = attr.ib(True)

    args_object = attr.ib(None)
    _makefile_fp = attr.ib(init=False)
    _dm_builder = attr.ib(attr.Factory(DMBuilder))
    _tempdir = attr.ib(None)

    def __attrs_post_init__(self):
        self._handle_args_object()

    def _handle_args_object(self):
        if self.args_object is None:
            return
        for attr_string in ['run', 'no_cleanup', 'jobs', 'touch', 'keep_going', 'always_make']:
            if attr_string in self.args_object:
                setattr(self, attr_string, getattr(self.args_object, attr_string))
        if "scheduler" in self.args_object:
            self._dm_builder.scheduler = SchedulingEngine[self.args_object.scheduler]
        if 'scheduler_args' in self.args_object and self.args_object.scheduler_args is not None:
            self._dm_builder.scheduler_args = shlex.split(self.args_object.scheduler_args)

    def add(self, target, deps, commands):
        self._dm_builder.add(target, deps, commands)

    def execute(self, callable=subprocess.Popen, popen_args=None):
        if popen_args is None:
            popen_args = {}
        with contextlib.ExitStack() as stack:
            if not self.no_cleanup:
                self.tempdir = stack.enter_context(remove_dir_on_exit(self.tempdir))
            makefile = os.path.join(self.tempdir, 'makefile')
            with open(makefile, 'wt') as makefile_fp:
                self._dm_builder.shell = self.shell
                self._dm_builder.write_to_filehandle(makefile_fp)

            makecmd = self.build_make_command(makefile)

            logger.warning(' '.join(makecmd))
            process = callable(' '.join(makecmd), shell=True, **popen_args)
            try:
                completed_process = process.communicate()
            except KeyboardInterrupt:
                process.send_signal(signal.SIGINT)
                message = 'Exiting after keyboard interrupt'
                if self.exit_on_keyboard_interrupt:
                    logger.warning(message)
                    exit()
                raise KeyboardInterrupt(message)
            logger.warning(' '.join(makecmd))

        return completed_process

    def build_make_command(self, makefile_name):
        makecmd = ['make', '-Werror']
        if not self.run:
            makecmd.append("-n")
        if self.keep_going:
            makecmd.append("-k")
        if self.question:
            makecmd.extend(["-q", self.question])
        if self.touch:
            makecmd.extend(["-t"])
        if self.debug:
            makecmd.append("-d")
        if self.always_make:
            makecmd.append("-B")
        makecmd.extend(["-j", str(self.jobs)])
        makecmd.extend(["-f", makefile_name])
        makecmd.append("all")
        return makecmd

    @property
    def tempdir(self):
        """Returns the temporary dir that is used during execute()

        Cleaned up after execute() if no_cleanup=False

        >>> dm = DistributedMake()
        >>> tempdir = dm.tempdir
        >>> os.path.exists(tempdir)
        True
        >>> dm.execute()
        (...)
        >>> os.path.exists(tempdir)
        False
        """
        if self._tempdir is None:
            self._tempdir = mkdtemp()
        return self._tempdir

    @tempdir.setter
    def tempdir(self, new_tempdir):
        self._tempdir = new_tempdir

    def get_tempfile(self):
        """Returns a tempfile that is cleaned up after execute() is called

        :returns: returns a tuple containing an OS-level handle to an open file
        (as would be returned by os.open()) and the absolute pathname of that file, in that order

        >>> dm = DistributedMake()
        >>> file_handle, file_name = dm.get_tempfile()
        >>> os.path.exists(file_name)
        True
        >>> dm.execute()
        (...)
        >>> os.path.exists(file_name)
        False

        The temporary file is not cleaned up when no_cleanup is set to True.
        >>> dm = DistributedMake(no_cleanup=True)
        >>> file_handle, file_name = dm.get_tempfile()
        >>> os.path.exists(file_name)
        True
        >>> dm.execute()
        (...)
        >>> os.path.exists(file_name)
        True

        """
        return mkstemp(dir=self.tempdir)


@contextlib.contextmanager
def remove_dir_on_exit(dir):
    yield dir
    shutil.rmtree(dir)
