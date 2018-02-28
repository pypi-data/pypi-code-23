# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import gettext
import os
import subprocess
from builtins import object
from builtins import str
from pathlib import Path

import matrix
import py.path
import tox
import voluptuous
from ngofile import list_files
from ngomodel import ClassWithSchema
from ngomodel import SchemaProperty
from ngomodel import assert_prop
from ngomodel import take_arrays
from ngomodel import validators

_ = gettext.gettext


class Environment(ClassWithSchema):
    schemaPath = "schemas/Environment.json"


class PythonEnvironment(Environment):
    schemaPath = "schemas/PythonEnvironment.json"

    def set_path(self, value):
        if value.is_dir():
            # need to look in subfolders
            ps = [value.joinpath(s) for s in ['.', 'bin', 'Scripts']]
            exes = list_files(
                ps, ['python*', 'pypy*'], ['*.dll', '*.so', '*.pdb'],
                raise_src_exists=False)
            # flatten
            exes = [x for xs in exes for x in xs]
            assert len(exes) > 0
            exes = [
                e for e in exes
                if e.suffix in [None, '.exe'] and not e.stem.endswith('w')
            ]
            assert len(exes) == 1
            value = exes[0]
        if not value.name.startswith('py'):
            raise InvalidValue(
                '%s is not a python executable or a python directory', value)
        self._validated('path', value)

    def __repr__(self):
        '''Returns representation of the object'''
        return "%s (%s %s)" % (self.__class__.__name__, self.version,
                               self.archi)

    def __str__(self):
        return '%s (%s python %s %s)' % (self.name, self.path.stem,
                                         self.version, self.archi)

    @property
    @assert_prop('path')
    def folder(self):
        """ returns the environment main folder as pathlib.Path or None """
        cur = self.path
        while cur.parent is not cur:
            if cur.joinpath('include').exists():
                return cur.resolve()
            cur = cur.parent

    @assert_prop('path')
    def update_from_pyexe(self):
        """ retrieve version/archi from python exectuable """
        pyexe = py.path.local(str(self._path))
        out = pyexe.sysexec("-c", "import sys; "
                            "print(list(sys.version_info)); "
                            "import platform;"
                            "print(platform.architecture()[0]);"
                            "print(sys.version);")
        lines = out.splitlines()
        ver = eval(lines.pop(0))
        self.version = '%i.%i.%i' % (ver[0], ver[1], ver[2])
        self.archi = lines.pop(0)
        self.versionLong = "\n".join(lines)

    @assert_prop('path')
    def pip_exe(self):
        exes = list_files(
            self.path, ['pip.exe', 'pip'], ['libs', 'Lib', 'tcl'],
            recursive=True)
        assert len(exes) == 1
        return exes[0].resolve()

    @assert_prop('path')
    def pip(self, command, *args):
        """ run a pip command on environment """
        cmds = [str(self.pip_exe), command]
        cmds += [str(a) for a in args]
        subprocess.call(cmds)

    @assert_prop('path')
    def install(self, *args):
        self.pip('install', *args)

    @property
    @assert_prop('path')
    def activation_script(self):
        self.script = self.folder.joinpath('Scripts', 'activate_this.py')
        if script.exists():
            raise Exception(
                'activation script cannot be located in %s' % str(self.path))
        return script.resolve()

    @assert_prop('path')
    def activate():
        cmds = [str(self.path), str(self.activation_script)]
        subprocess.call(cmds)


class ToxEnvironment(Environment):
    schemaPath = "schemas/ToxEnvironment.json"

    def set_path(self, value):
        if value.is_dir():
            value = value.joinpath('setup.cfg')
            if not value.exists():
                raise FileNotFoundError(
                    'setup.cfg not found in %s' % str(value))
        if not value.name.startswith('setup.cfg'):
            raise FileNotFoundError(
                'path does not link to a configuration file')
        self._validated('path', value)
        cwd = os.getcwd()
        os.chdir(str(value.parent))
        self.config = tox.config.parseconfig([])
        os.chdir(cwd)
        self.update_from_config()

    @assert_prop('config')
    def list_env(self, all=False):
        if all:
            return list(self.config.envconfigs.keys())
        return [
            e for e in list(self.config.envconfigs.keys())
            if e not in ['clean', 'check', 'report', 'docs']
        ]

    @assert_prop('config')
    def update_from_config(self):
        self.pythonEnvs.clear()
        for (alias, conf) in list(matrix.from_file(str(self.path)).items()):
            version = conf["python_versions"]
            deps = conf["dependencies"]
            envVars = conf["environment_variables"]
            self.logger.info('UPDATE found python %s %s' % (alias, version))
            self.pythonEnvs[alias] = PythonEnvironment(
                path=self.config.toxworkdir.join(alias),
                version=version,
                deps=deps,
                envVars=envVars)

    @assert_prop('path')
    def update_from_dir(self):
        self.pythonEnvs = {
            e.folder.name: PythonEnvironment(e)
            for e in self.envs if e.py_exe
        }
