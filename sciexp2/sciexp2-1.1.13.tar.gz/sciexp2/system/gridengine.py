#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch and monitor gridengine jobs."""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import os
import subprocess
import warnings

import sciexp2.system
import sciexp2.common.instance
from sciexp2.common import progress


class System (sciexp2.system.System):
    """Manage jobs in a gridengine system."""

    STATE_CMD = ["qstat", "-r"]

    ASSUMES = ["JOB_NAME", "STDOUT", "STDERR"]
    DEFINES = []

    def compute_state(self):
        # check program exists
        try:
            subprocess.check_output([self.STATE_CMD[0], "-help"])
            exists = True
        except OSError as e:
            warnings.warn("Could not run %s; assuming no job is running: %s" %
                          (self.STATE_CMD[0], str(e)))
            exists = False

        # compute set of running jobs
        running = set()
        if exists:
            pipe = subprocess.Popen(self.STATE_CMD,
                                    stdout=subprocess.PIPE)
            for line in pipe.stdout:
                line = line.split()
                if line[0] == "Full" and line[1] == "jobname:":
                    running.add(line[2])
            if pipe.wait() != 0:
                raise Exception("Could not get execution state ('%s'): %s" %
                                (" ".join(self.STATE_CMD), pipe.returncode))

        # build instance group of job states
        self._jobs = sciexp2.common.instance.InstanceGroup()
        for instance in self._launchers:
            if instance["JOB_NAME"] in running:
                job = Job(self,
                          sciexp2.system.Job.RUNNING,
                          instance)
            else:
                job = Job(self,
                          sciexp2.system.Job.compute_state(self, instance),
                          instance)
            self._jobs.add(job)

    @staticmethod
    def post_generate(base, path, instance, xlator):
        def ensure_dirs(var):
            val = xlator.xlate_rec(instance[var], instance)
            if not os.path.isabs(val):
                val = os.sep.join([base, val])
            val_dir = os.path.dirname(val)
            if not os.path.exists(val_dir):
                os.makedirs(val_dir)
            else:
                assert os.path.isdir(val_dir)
        ensure_dirs("DONE")
        ensure_dirs("FAIL")


class Job (sciexp2.system.Job):
    """A job in a gridengine system."""

    def state(self):
        state = self["_STATE"]
        if state == sciexp2.system.Job.RUNNING:
            name = self["JOB_NAME"]
        elif state == sciexp2.system.Job.DONE:
            name = self._system.get_relative_path(self["DONE"])
        elif state == sciexp2.system.Job.FAILED:
            name = self._system.get_relative_path(self["FAIL"])
        elif state in [sciexp2.system.Job.NOTRUN, sciexp2.system.Job.OUTDATED]:
            name = self._system.get_relative_path(self["LAUNCHER"])
        else:
            raise ValueError("Unknown job state: %r" % state)
        return state, name

    def submit(self, *args):
        launcher = os.sep.join([self._system._base, self["LAUNCHER"]])
        assert os.path.isfile(launcher)
        cmd = ["qsub"] + self._submit_args(args) + [launcher]
        progress.verbose(" %s", " ".join(cmd))
        if progress.level() < progress.LVL_DEBUG:
            subprocess.check_call(cmd,
                                  stdout=sciexp2.system._DEVNULL,
                                  stderr=subprocess.STDOUT)
        else:
            subprocess.call(cmd)

    def kill(self, *args):
        launcher = os.sep.join([self._system._base, self["LAUNCHER"]])
        assert os.path.isfile(launcher)
        cmd = ["qdel"] + self._kill_args(args) + [launcher]
        progress.verbose(" %s", " ".join(cmd))
        if progress.level() < progress.LVL_DEBUG:
            subprocess.check_call(cmd,
                                  stdout=sciexp2.system._DEVNULL,
                                  stderr=subprocess.STDOUT)
        else:
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
