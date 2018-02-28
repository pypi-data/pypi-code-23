# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 11:06:57 2012

@author: cedric
"""
from __future__ import unicode_literals

import gettext
import logging
import pathlib
import subprocess
import importlib
import inspect
import sys
import os
import pprint
from glob import glob
from builtins import str
from datetime import datetime
from collections import OrderedDict

from xml.etree import ElementTree as ET
import docker
import py.path
import voluptuous
from future.builtins import object
from future.utils import native
from ngofile import list_files
from ngomodel import ClassWithSchema
from ngomodel import ObjectManager
from ngomodel import assert_prop
from ngomodel import inspect_file
from ngomodel import root_namespace
from ngomodel import take_arrays
from ngomodel import FunctionInspector
from ngomodel import ClassInspector

from ngomodel.validators import _validators as validators
from ngomodel.validators import prettify
from ngomodel._json import JsonParser
from ngomodel._yaml import YamlParser
from ngomodel._jinja2 import Jinja2Serializer

from ._cookiecutter import CookiecutterManager
from ._environment import PythonEnvironment
from ._environment import ToxEnvironment
from ._file import File
from ._vs2017 import Vs2017Serializer

_ = gettext.gettext

TEMPLATE_CHOICES = (
    ('python', 'file.py'),
    ('py', 'file.py'),
    ('pyclass', 'file_class.py'),
    ('class-python', 'file_class.py'),
    ('class-cpp', 'file_class.cpp'),
    ('cpp', 'file.cpp'),
    ('test-py', 'file_test.py'),
    ('test-cpp', 'file_test.cpp'),
)



TEMPLATE_CHOICES_DICT = {c[0]: c[1] for c in TEMPLATE_CHOICES}


class Project(ClassWithSchema):
    schemaPath = "schemas/Project.json"

    def __init__(self, name=None, **kwargs):
        if name:
            kwargs['name'] = name
        ClassWithSchema.__init__(self, **kwargs)
        kwargs.pop('name')
        if name is None:  # look for setup.py
            # all the magic is in self.repoDir, which calls a property that will detect the best setup.py
            rp = self.repoDir if self.repoDir else pathlib.Path('.')
            ls = list_files(rp, 'setup.py', recursive=False, in_parents=True)
            if ls:
                self.setup_py = ls[0].resolve()
                self.logger.info(
                    _('INIT found project setup %s' % self.setup_py))
                self.update_from_setup()
        elif not kwargs:
            pm = ProjectManager()
            if not pm.loaded: pm.update_from_files()
            if pm.has_object(name):
                o = pm.get_object(name)
                self.update(**o.validated)
                self.logger.info(
                    _('INIT found project details in registry %s\n%s' %
                      (pm, prettify(self.validated))))
            else:
                cm = CookiecutterManager()
                if not cm.loaded: cm.update_from_files()
                for c in cm._objects.values():
                    if c.project_name == name:
                        o = c.transform_to(Project)
                        self.update(**o.validated)
                        # TEMP
                        self.repoDir = c.filePath.with_name(c.repo_name)
                        self.logger.info(
                            _('INIT found project details in registry %s\n%s' %
                              (cm, prettify(self.validated))))
        if self.repoDir:
            self.fileSrcManager.pathlist = [self.repoDir.joinpath('src')]
            self.fileTestManager.pathlist = [self.repoDir.joinpath('tests')]
            self.fileDataManager.pathlist = [self.repoDir]

    @assert_prop('setup.py')
    def update_from_setup(self):
        pyexepath = py.path.local(sys.executable)
        reload(
            sys
        )  # special trick to call setdefaultencoding https://stackoverflow.com/questions/2276200/changing-default-encoding-of-python#
        sys.setdefaultencoding('UTF8')
        out = pyexepath.sysexec(
            str(self.setup_py), '--name', '--version', '--author',
            '--author-email', '--url', '--description', '--requires')
        o = tuple(out.split('\n'))
        name, version, authorName, authorEmail, url, description, requires = o[
            0:7]
        self.repoDir = self.setup_py.parent
        self.name = name.strip()
        self.version = version.strip()
        self.authorName = authorName.strip()
        self.authorEmail = authorEmail.strip()
        self.website = url.strip()
        self.description = description.strip()

    def repoDir(self):
        rn = validators.BaseString(self.repoName)
        #if rn and self.projectDir and self.projectDir.joinpath(rn).exists():
        #    return self.projectDir.joinpath(rn).resolve()
        if self.filePath: return self.filePath.parent.resolve()

    def set_repoDir(self, value):
        self.fileSrcManager.pathlist = [self.repoDir.joinpath('src')]
        self.fileTestManager.pathlist = [self.repoDir.joinpath('tests')]
        self.fileDataManager.pathlist = [self.repoDir]

    def repoName(self):
        p = self.repoDir
        if p: return p.name

    def setup_py(self):
        p = self.repoDir
        if p and p.joinpath('setup.py').exists():
            return p.joinpath('setup.py').resolve()

    def set_setup_py(self, value):
        self.repoDir = value.parent

    def tox_ini(self):
        p = self.repoDir
        if p and p.joinpath('tox.ini').exists():
            return p.joinpath('tox.ini').resolve()
        p = self.setup_py
        if p and p.with_name('tox.ini').exists():
            return p.with_name('tox.ini').exists()

    def toxEnv(self):
        o = ToxEnvironment()
        if not o.path and self.tox_ini:
            o.path = self.tox_ini.parent
        self.toxEnv = o
        return o

    @property
    def package(self):
        """ function to retrieve corresponding package """
        #from ngomodel import NgoLibrary
        #pck = NgoLibrary().package(self.name)
        return None
        if pck is None:
            pck = NgoLibrary().package(self.alias)
        return pck

    def vsGuid(self):
        if self.pyproj:
            root = ET.parse(self.pyproj.open('r'))
            nsmap = root_namespace(root)[1:-1]
            return root.find('.//{%s}ProjectGuid' % nsmap).text

    @property
    def pyproj(self):
        pyproj = self.repoDir.joinpath('%s.pyproj' % self.name)
        if pyproj.exists():
            return pyproj

    def pythonEnvs(self):
        if self.tox_ini:
            return self.toxEnv.pythonEnvs

    def build(self):
        """ build the project according to tox.ini or premake """
        if self.repoDir.joinpath('premake4.lua').exists():
            self.logger.info(_('rebuild distribution according to premake4.lua'))
            wd = self.repoDir.relative_to(self.repoDir.anchor).as_posix()
            self.docker('premake4 gmake',working_dir='/app/%s'%wd)
            self.docker('make config=release64 all',working_dir='/app/%s/build'%wd)
        if self.tox_ini:
            self.logger.info(_('rebuild distribution specified in Tox'))
            config = self.toxEnv.config
            for f in list_files(self.repoDir,'src/*.egg-info/*'):
                os.remove(str(f))
            proc = subprocess.Popen('tox -e check', cwd=str(self.repoDir))
            proc.wait()
            subprocess.call([
                'python',
                str(self.setup_py), 'sdist', 'bdist_wheel', '--dist-dir',
                str(config.distdir)
            ])

    def futurize(self, stage=0, *args):
        """ execute futurize with input stage

        unicode by default, 
        :param stage: 1 safe fixes, 2 py3 style wrapped for py2, 0 both
        :type stage: int
        """
        self.logger.info(_('run FUTURIZE with stage %i' % stage))
        cmds = ['futurize', '-%i' % stage, '-u', '-w']  # default options
        cmds += [str(a) for a in args]
        srcs = self.fileSrcManager.list_files()
        tests = self.fileTestManager.list_files()
        cmds += [str(f) for f in srcs + tests]
        proc = subprocess.Popen(cmds, cwd=str(self.repoDir))
        proc.wait()

    def clean_imports(self, *args):
        """ execute ISORT and autoflake to clean imports in source files """
        self.logger.info(_('run ISORT to sort imports'))
        cmds = ['isort', '--verbose', '--recursive']  # default options
        cmds += [str(a) for a in args]
        srcs = self.fileSrcManager.list_files()
        tests = self.fileTestManager.list_files()
        cmds += [str(f) for f in srcs + tests]
        subprocess.call(cmds)
        self.logger.info(_('run AUTOFLAKE to remove unused imports'))
        cmds = ['autoflake', '-r', '-i']  # default options
        cmds += [str(a) for a in args]  # should put additional checks
        if self.deps:
            cmds += [','.join(self.deps)]
        cmds += [str(f) for f in srcs + tests]
        proc = subprocess.Popen(cmds, cwd=str(self.repoDir))
        proc.wait()

    def format_code(self, *args):
        """ execute YAPF to clean imports in source files """
        self.logger.info(_('run YAPF to format code'))
        cmds = ['yapf', '-i', '-r']  # default options
        cmds += [str(a) for a in args]
        srcs = self.fileSrcManager.list_files()
        tests = self.fileTestManager.list_files()
        cmds += [str(f) for f in srcs + tests]
        proc = subprocess.Popen(cmds, cwd=str(self.repoDir))
        proc.wait()

    def py23(self):
        """ execute futurize, clean_imports and format_code """
        self.futurize()
        self.clean_imports()
        self.format_code()

    def update_pyproj(self, *args):
        """ update Visual Studio 2017 project file """
        self.logger.info(_('create/update project for Visual Studio 2017'))
        from ._vs2017 import Vs2017Serializer
        pyproj = self.pyproj or self.repoDir.joinpath('%s.pyproj' % self.name)
        Vs2017Serializer().dump(pyproj, self, *args)

    def premake4(self,target='gmake'):
        """ execute premake4 """
        pm = ProjectManager()
        if pm.premakeDir:
            cmd = str(pm.premakeDir.joinpath('premake4'))
        else:
            cmd = 'premake4'
        cmds = [cmd, target, self.repoDir]
        proc = subprocess.Popen(cmds, cwd=str(self.repoDir))
        proc.wait()

    def package(self):
        self.create_apipkg()
        self.create_click()
        self.py23()
        self.build()

    def create_pypirc(self,username=None,password=None):
        """ create .pypirc file containing pypi identifiers """
        pm = ProjectManager()
        if username is None:
            username = pm.serverUsername
            if username is None:
                raise Exception('no username found for server %s'%server)
        if password is None:
            password = pm.serverPassword
        if password is None:
            raise Exception('no password found for server %s'%server)
        pypirc = pathlib.Path(os.path.expanduser('~'),'.pypirc')
        Jinja2Serializer('.pypirc').dump(pypirc,{'username':username,'password':password})

    def register(self):
        """ register python project on pypi """
        config = self.toxEnv.config
        for f in list_files(config.distdir,'*.whl'):
            subprocess.call([
                'twine', 'register', str(f)])

    def publish(self):
        """ publish python project on pypi """
        config = self.toxEnv.config
        for f in list_files(config.distdir,'*.whl'):
            subprocess.call([
                'twine', 'upload', str(f)])

    @property
    def envVars(self):
        pm = ProjectManager()
        ev = pm.envVars
        ev[self.envVar] = self.repoDir
        for d in self.deps:
            if pm.has_object(d):
                d2 = pm.get_object(d)
                ev[d2.envVar] = d2.repoDir
        return ev

    @property
    def volumes(self):
        """ volumes to be mounted

        :rtype: List """
        to_expose = []
        def common_root(p1,p2):
            n = min(len(p1.parts),len(p2.parts))
            ret = [p1 for p1,p2 in zip(p1.parts,p2.parts) if p1==p2]
            if len(ret)>1:
                return pathlib.Path(*ret)
        for p in self.envVars.values():
            for r in to_expose:
                if common_root(p,r):
                    to_expose.remove(r)
                    to_expose.append(common_root(p,r))
            if not any([common_root(p,r) for r in to_expose]):
                to_expose.append(p)
        return to_expose

    def docker(self,*extra_cmds,**options):
        """ execute a list of commands on a docker container

        the default image is "numengo/build-x64" but can be changed with options['dockerimage']

        :param cmds: list of commands to run on container
        :type cmds: str
        :param options: options to create container (in docker-py run options)
        """
        dockerimage = options.pop('dockerimage','numengo/build-x64:latest')
        volumes = ['%s:/app/%s'%(v.as_posix(),v.relative_to(v.anchor).as_posix()) for v in self.volumes]
        environment = ['%s=/app/%s'%(e,v.relative_to(v.anchor).as_posix()) for e,v in self.envVars.items()]

        client = docker.from_env()
        cmd = '&&'.join(extra_cmds)
        self.logger.info(_('run command "%s" on %s'%(cmd,dockerimage)))
        container = client.containers.run(dockerimage,
                       volumes=volumes,
                       detach=True,
                       tty=True,
                       environment=environment,
                       command=cmd,**options)
        resp = container.wait()
        if resp['StatusCode'] == 0:
            self.logger.warning(container.logs(stdout=True,stderr=True))
        else:
            raise Exception('container %s exited with code %i for command %s.\n%s'%(
                container,resp['StatusCode'],cmd,container.logs(stdout=True,stderr=True)))
        container.stop()
        container.remove()

    def create_click(self):
        """ create the api for click """
        ep = {e.split('=')[0].strip(): e.split('=')[1].strip()
              for e in self.entryPoints}
        epc = {}
        epf = {}
        for k, v in ep.items():
            m, p = v.split(':')
            m =importlib.import_module(m)
            p = getattr(m,p)
            if inspect.isfunction(p):
                epf[k] = FunctionInspector(p)
            elif inspect.isclass(p):
                ci = ClassInspector(p)
                # remove all update functions
                for mn, m in ci.methods.items():
                    if mn.startswith('update'):
                        ci.methods.pop(mn)
                epc[k] = ci
        fp = self.repoDir.joinpath('src',self.packageName,'cli.py')
        Jinja2Serializer('cli.py').dump(fp,[self,{'classes': epc, 'functions': epf}])

    def create_apipkg(self):
        """ create the namespace for apipkg """
        src = self.repoDir.joinpath('src',self.packageName)
        ds = [l.parent for l in list_files(src, '*.py', excludes='templates',recursive=True)]
        ds = list(set(ds))
        for d in ds:
            pkg_dict = OrderedDict()
            for l in list_files(d,'*.py',excludes=['__*.py','templates','cli.py']):
                fs, cs, vs = inspect_file(l)
                for i in cs+fs+vs:
                    if not i.startswith('_'):
                        p = str(l.relative_to(d).as_posix())[0:-3].replace('/','.')
                        pkg_dict[i] = ".%s:%s"%(p,i)
            pkg = d.relative_to(src.parent).as_posix().replace('/','.')
            fp = d.joinpath('_apipkg.py')
            Jinja2Serializer('_apipkg.py').dump(fp,[self,{'pkg':pkg, 'pkg_dict':pkg_dict}])

    def create_file(self, filetype, name):
        """ create a new file with a given template
    
        :param filetype: type of file
        :type filetype: py, pyclass, class-python, class-cpp, cpp, test-py, test-cpp
        :param name: name of the file
        :type name: string

        :rtype: ngoproject.File
        """

        if not filetype in list(TEMPLATE_CHOICES_DICT.keys()):
            raise ValueError('filetype should be in %r' % list(
                TEMPLATE_CHOICES_DICT.keys()))
        template = TEMPLATE_CHOICES_DICT[filetype]
        tdir = 'src' if not filetype.startswith('test') else 'tests'
        tdir = self.repoDir.joinpath(tdir,
                                     validators.BaseString(
                                         self.packageName.strip()))
        if not '.' in name:
            ext = '.' + template.rsplit('.', 1)[1]
            name = name + ext
        else:
            ext = '.' + pathlib.Path(name).suffix
        fp = tdir.joinpath(name)

        fobj = File(
            name=name,
            extension=ext,
            template=template,
            path=fp,
            created=datetime.now())

        self.logger.info(_('create new file %s %s' % (filetype, fp)))
        Jinja2Serializer(template).dump(fp, fobj)
        return fobj

    def bumpversion(self,level='patch'):
        """ bump project version harcoded in project files
        :param level: bump to patch/minor/major
        :type level: 'patch','minor','major'
        """
        subprocess.Popen('bumpversion %s'%level, cwd=str(self.repoDir))

class ProjectManager(ObjectManager):
    parsers = [YamlParser, JsonParser]
    serializers = [Vs2017Serializer]
    extensions = ['.ngoprj']
    server = validators.StringOrNone
    serverUsername = validators.StringOrNone
    serverPassword = validators.StringOrNone
    premakeDir = validators.DirPathOrNone
    rootDir = validators.DirPathOrNone

    def __init__(self, *args, **kwargs):
        ObjectManager.__init__(self, Project, *args, **kwargs)
        self.logger = logging.getLogger(__name__)

    @property
    def envVars(self):
        if self.rootDir:
            return {
                #"DirRoot"           : self.rootDir,
                "BOOST_ROOT" : pathlib.Path('/usr/include/boost'),
                "DirProjectUnitTestRoot": self.rootDir.joinpath("projects","UnitTest"),
                "DirToolsroot"      : self.rootDir.joinpath("tools"),
                "DirOutputRoot"     : self.rootDir.joinpath("bin"),
                "DirLibraryRoot"    : self.rootDir.joinpath("lib"),
                "DirIncludeRoot"    : self.rootDir.joinpath("include"),
                "DirProjectsRoot"   : self.rootDir.joinpath("projects"),
                "DirScriptsRoot"    : self.rootDir.joinpath("scripts"),
                "DirDistribRoot"    : self.rootDir.joinpath("distrib"),
                'DirProjectNgoModelRoot' : self.rootDir.joinpath("projects","NgoModel"),
                }
        else:
            return {}

