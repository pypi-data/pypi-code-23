#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Execution system and job abstractions.

Each execution system consists of a Python module with:

* a subclass of `System` named ``System``.

* a subclass of `Job` that ``System`` will use.

Execution systems are searched for in the paths listed in :data:`SEARCH_PATH`,
where you can add new directories if necessary.

.. autodata:: sciexp2.system.SEARCH_PATH
"""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import abc
import glob
import imp
import os
import shutil
import six
import weakref

import sciexp2.common.instance
import sciexp2.common.filter
from sciexp2.common import varref


#: Paths to search for available execution systems.
#:
#: The order of the list establishes which execution system implementation will
#: be used in case it exists in more than one directory.
#:
#: Includes the current directory and the `system` directory shipped with
#: SciExp².
SEARCH_PATH = [
    os.curdir,
    os.path.dirname(__file__),
    ]


_TOKENIZER = varref.Tokenizer("@")
_DICTXLATOR = varref.DictXlator("@")


_DEVNULL = open("/dev/null", "w")


class SystemError (Exception):
    """Error loading system."""
    def __init__(self, message):
        Exception.__init__(self, message)


class SubmitArgsError (Exception):
    """Error translating job submission arguments."""
    def __init__(self, variables):
        Exception.__init__(
            self,
            "Found non-exported variables in job submission arguments: " +
            ", ".join(variables))


class System (six.with_metaclass(abc.ABCMeta)):
    """Abstract job manager.

    Each system must implement the abstract methods defined in this class
    and define two class attributes:

        ========= =======================================================
        Name      Description
        ========= =======================================================
        `ASSUMES` List of variables that are assumed to be present in the
                  launchers instance group for the system to work.
        `DEFINES` List of variables that the system internally defines and thus
                  must not be present in the launchers instance group.
        ========= =======================================================

    See also
    --------
    compute_state

    """

    ASSUMES = ["LAUNCHER", "DONE", "FAIL"]
    DEFINES = ["_STATE", "LAUNCHER_BASE"]

    def __init__(self, base_path, launchers, depends, submit_args):
        """
        Parameters
        ----------
        base_path : str
            Base directory where launchers are located.
        launchers : InstanceGroup
            Group describing the launchers.
        depends : sequence of str
            Variable names to which jobs depend.
        submit_args : sequence of str
            Extra arguments to the job-submitting program.

        """
        self._base = base_path
        self._base_abs = os.path.realpath(self._base)
        assert os.path.isdir(self._base_abs)
        self._launchers = launchers
        for assume in self.assumes():
            if assume not in self._launchers and len(self._launchers) > 0:
                raise ValueError("Variable '%s' must be present" % assume)
        for define in self.defines():
            if define in self._launchers:
                raise ValueError("Variable '%s' must not be present" % define)
        self._jobs = None
        self._depends = set(depends)
        self._submit_args = [
            _DICTXLATOR.xlate(i, {"LAUNCHER_BASE": self._base_abs},
                              allow_unxlated=True)
            for i in submit_args]
        self._submit_args_xlate = len([_TOKENIZER.vars(i)
                                       for i in self._submit_args]) > 0

    def get_relative_path(self, path, cwd=None):
        """Get path (relative to base) as relative to `cwd`."""
        if cwd is None:
            cwd = os.getcwd()
        if not os.path.isabs(path):
            path = os.path.join(self._base_abs, path)
        return os.path.relpath(path, cwd)

    def build(self, types, *filters):
        """Generate a sequence with the jobs matching the given criteria.

        Parameters
        ----------
        types : set
            Set of states that the jobs must be on.
        filters : list of filters
            List of filters that the jobs must match.

        See also
        --------
        Job

        """
        self.compute_state()

        build_filter = sciexp2.common.filter.Filter(*filters)

        if len(types) > 0:
            state_filter = "||".join(["_STATE == '%s'" % state
                                      for state in types
                                      if state != "inverse"])
            if "inverse" in types:
                state_filter = "!(%s)" % state_filter
            build_filter += sciexp2.common.filter.Filter(state_filter)

        if len(self._jobs) > 0:
            build_filter.validate(set(self._jobs.variables()))
            return self._jobs.select(build_filter)
        else:
            return sciexp2.common.instance.InstanceGroup()

    @classmethod
    def assumes(cls):
        """The set of variables that must be present on the launchers."""
        return set(System.ASSUMES + cls.ASSUMES)

    @classmethod
    def defines(cls):
        """The set of variables that must not be present on the launchers."""
        return set(System.DEFINES + cls.DEFINES)

    @abc.abstractmethod
    def compute_state(self):
        """Compute the current state of jobs.

        The implementation must set the ``_jobs`` attribute with an
        InstanceGroup of `Job` instances. This can be computed using the
        contents of the ``_launchers`` attribute.

        """
        pass

    @staticmethod
    def post_generate(base, path, instance, xlator):
        """Post-process the generation of file `path`."""
        pass


class Job (six.with_metaclass(abc.ABCMeta, sciexp2.common.instance.Instance)):
    """Abstract job descriptor.

    Each job must implement the abstract methods defined in this class.

    See also
    --------
    state, submit, kill

    """

    # job states
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    OUTDATED = "outdated"
    NOTRUN = "notrun"

    STATES = [
        RUNNING,
        DONE,
        FAILED,
        OUTDATED,
        NOTRUN,
    ]

    STATE_SHORT = {
        RUNNING:  "R",
        DONE:     "D",
        FAILED:   "F",
        OUTDATED: "O",
        NOTRUN:   "N",
        }

    STATE_LONG = {
        RUNNING:  "Running",
        DONE:     "Done",
        FAILED:   "Failed",
        OUTDATED: "Outdated",
        NOTRUN:   "Not run",
        }

    def __init__(self, system, state, instance):
        """
        Parameters
        ----------
        system : System
            System for which this job is.
        state : str
            Execution state of the job.
        instance : str
            Launcher instance describing this job.

        """
        sciexp2.common.instance.Instance.__init__(self, instance)
        self["_STATE"] = state
        self._system = weakref.proxy(system)

    def __repr__(self):
        return repr(sciexp2.common.instance.Instance(self))

    @classmethod
    def compute_state(cls, system, instance):
        """Generic job state computation.

        Parameters
        ----------
        system : System
            System for which this job is being checked.
        instance
            Launcher instance describing a job.

        Returns
        -------
        Generic job state according to the failed/done files; otherwise returns
        `NOTRUN`.

        """
        fail_path = instance["FAIL"]
        if not os.path.isabs(fail_path):
            fail_path = os.sep.join([system._base, fail_path])
        if os.path.exists(fail_path):
            return cls.FAILED

        done_path = instance["DONE"]
        if not os.path.isabs(done_path):
            done_path = os.sep.join([system._base, done_path])
        if not os.path.exists(done_path):
            return cls.NOTRUN

        done_mtime = os.stat(done_path).st_mtime
        for dep in system._depends:
            path = instance[dep]
            if path == "":
                continue
            if not os.path.isabs(path):
                path = os.sep.join([system._base, path])
            if not os.path.exists(path) or \
               done_mtime < os.stat(path).st_mtime:
                return cls.OUTDATED
        return cls.DONE

    @abc.abstractmethod
    def state(self):
        """Return a string describing the job and its state."""
        pass

    @abc.abstractmethod
    def submit(self, *args):
        """Submit a job to execution."""
        pass

    def _submit_args(self, args):
        """Return extra arguments for the job submitting program."""
        if not self._system._submit_args_xlate and \
           len([_TOKENIZER.vars(i) for i in args]) == 0:
            return self._system._submit_args + list(args)

        instance = dict(self)
        instance["LAUNCHER_BASE"] = self._system._base_abs
        try:
            return [_DICTXLATOR.xlate_rec(i, self)
                    for i in self._system._submit_args + list(args)]
        except varref.XlateError as e:
            raise SubmitArgsError(e.variables)

    @abc.abstractmethod
    def kill(self, *args):
        """Kill a job from execution."""
        pass

    def _kill_args(self, args):
        """Return extra arguments for the job killing program."""
        if len([_TOKENIZER.vars(i) for i in args]) == 0:
            return list(args)

        instance = dict(self)
        instance["LAUNCHER_BASE"] = self._system._base_abs
        try:
            return [_DICTXLATOR.xlate_rec(i, self)
                    for i in list(args)]
        except varref.XlateError as e:
            raise SubmitArgsError(e.variables)


def get(name):
    """Get an execution system implementation by name.

    See also
    --------
    SEARCH_PATH

    """
    try:
        info = imp.find_module(name, SEARCH_PATH)
        system = imp.load_module(name, *info)
    except ImportError:
        raise SystemError("Unknown system %r" % name)
    try:
        res = system.System
    except AttributeError:
        raise AttributeError("Does not look like an execution " +
                             "system implementation: %s" % name)
    res.name = name
    return res
