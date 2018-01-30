# -*- coding: utf-8 -*-
import os
import sys
import ast
import re
import shutil
import subprocess as sp
import hashlib
import yaml
import glob
import pytest
import logging
from distutils.version import StrictVersion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONDA_DEFAULT_INSTALL_DIR = os.path.join(os.getenv("HOME"), ".conda_env")


class WorkflowEngineException(Exception):
    pass


def environment_files(path, testdir, filters=()):
    retval = []
    for path, dirs, files in os.walk(path):
        if path.startswith(testdir):
            continue
        if ".conda" in path:
            continue
        for f in files:
            if any(f == flt for flt in filters):
                retval += [os.path.normpath(os.path.join(path, f))]
    return retval


def addoption(parser, engine="snakemake"):
    """Helper function to add options to pytest.

    Call this function from a :py:meth:`pytest_addoption` hook

    Usage:

    .. code-block:: python

       from lts_workflows.pytest import plugin

       def pytest_addoption(parser):
          group = parser.getgroup("lts_workflows_sm_scrnaseq",
                                  "single cell rna sequencing options")
          plugin.addoption(group)

    """
    parser.addoption("--no-slow", action="store_true",
                     help="don't run slow tests", default=False,
                     dest="no_slow")
    parser.addoption("-H", "--hide-workflow-output", action="store_true",
                     help="hide workflow output",
                     dest="hide_workflow_output", default=False)
    parser.addoption("-T", "--threads", action="store",
                     default="1",
                     help="number of threads to use",
                     dest="threads")
    parser.addoption("--enable-test-conda", action="store_true",
                     help="enable test conda setup; automatically install all dependencies in semi-persistent test conda environments",
                     dest="enable_test_conda", default=False)
    parser.addoption("--conda-install-dir", action="store",
                     default=CONDA_DEFAULT_INSTALL_DIR,
                     help="set conda install dir",
                     dest="conda_install_dir")
    parser.addoption("--conda-update", action="store_true",
                     help="update local conda installation",
                     default=False, dest="conda_update")
    if engine == "snakemake":
        parser.addoption("-2", "--python2-conda", action="store",
                         default="py2.7",
                         help="name of python2 conda environment [default: py2.7]",
                         dest="python2_conda")
        parser.addoption("-C", "--use-conda", default=False,
                         action="store_true",
                         help="pass --use-conda flag to snakemake workflows; will install conda environments on a rule by rule basis",
                         dest="use_conda")
    elif engine == "nextflow":
        parser.addoption("-N", "--nextflow-conda", action="store",
                         default="nextflow",
                         help="name of nextflow conda environment [default: nextflow]",
                         dest="nextflow_conda")
    else:
        raise WorkflowEngineException("no such workflow engine '{}' supported".format(engine))


def namespace(engine="snakemake", **kwargs):
    m = re.search("--conda-install-dir\s+(?P<conda_install_dir>\w+)",
                  " ".join(sys.argv))
    install_dir = m.group("conda_install_dir") if m else CONDA_DEFAULT_INSTALL_DIR
    python2 = conda_create_env(name="python2", envlist=kwargs.get('py2', []),
                               install_dir=install_dir, name_only=True)
    python3 = conda_create_env(name="python3", envlist=kwargs.get('py3', []),
                               install_dir=install_dir, name_only=True)
    if engine == "snakemake":
        retval = {
            'conda_env_active': python3,
            'conda_env_list': (
                ('python2', python2, kwargs.get('py2', [])),
                ('python3', python3, kwargs.get('py3', [])),
            ),
        }
    elif engine == "nextflow":
        nextflow = conda_create_env(name="nextflow",
                                    envlist=kwargs.get('nextflow', []),
                                    install_dir=install_dir, name_only=True)
        retval = {
            'conda_env_active': nextflow,
            'conda_env_list': (
                ('nextflow', nextflow, kwargs.get('nextflow', [])),
                ('python2', python2, kwargs.get('py2', [])),
                ('python3', python3, kwargs.get('py3', [])),
            ),
        }
    else:
        raise WorkflowEngineException("no such workflow engine '{}' supported".format(engine))
    return retval


def slow_runtest_setup(item):
    """Skip tests if they are marked as slow and --no-slow is given"""
    if getattr(item.obj, 'slow', None) and item.config.getvalue('no_slow'):
        pytest.skip('slow tests not requested')


def report_header(config, engine="snakemake"):
    if engine == "snakemake":
        return _snakemake_report_header(config)
    elif engine == "nextflow":
        return _nextflow_report_header(config)
    else:
        raise WorkflowEngineException("no such workflow engine '{}' supported".format(engine))


def _snakemake_report_header(config):
    try:
        output = sp.check_output(['conda', 'env', 'list', '--json'])
        envs = ast.literal_eval(output.decode("utf-8"))
        py2 = [x for x in envs['envs'] if re.search("{}{}$".format(
            os.sep, config.option.python2_conda), x)][0]
        py2bin = os.path.join(py2, "bin")
        os.environ["PATH"] = ":".join([os.environ["PATH"], py2bin])
        py2str = "python2: {}".format(py2bin)
    except:
        py2str = logger.warn("No conda python2 environment found! Workflow tests depending on python2 programs will fail!")
    if not pytest.config.option.enable_test_conda or pytest.config.option.use_conda:
        conda = []
    else:
        conda = ["conda environments:"] + \
                ["  {}: {}".format(name, path) for (name, path, env) in pytest.conda_env_list]
    basetemp = ["basetemp: {}".format(pytest.config.option.basetemp)]
    return "\n".join([py2str] + conda + basetemp)


def _nextflow_report_header(config):
    try:
        output = sp.check_output(['conda', 'env', 'list', '--json'])
        envs = ast.literal_eval(output.decode("utf-8"))
        nf = [x for x in envs['envs'] if re.search("{}{}$".format(
            os.sep, config.option.nextflow_conda), x)][0]
        nfbin = os.path.join(nf, "bin")
        os.environ["PATH"] = ":".join([os.environ["PATH"], nfbin])
        nfstr = "nextflow: {}".format(nfbin)
    except:
        nfstr = logger.warn("No conda nextflow environment found! Workflow tests depending on nextflow will fail!")
    basetemp = ["basetemp: {}".format(pytest.config.option.basetemp)]
    return "\n".join([nfstr] + basetemp)


##############################
# Create environments
##############################
def conda_create_env(name, envlist, install_dir=CONDA_DEFAULT_INSTALL_DIR,
                     disable=False, name_only=False, package_path=None,
                     **kwargs):
    """Create local conda environments for all tests.

    Most packages live in a python3 environment. nextflow lives in its
    own environment due to java-sdk version conflict with gatk.

    Args:
      name: environment name
      envlist: list of environment files
      install_dir: conda installation directory
      disable: disable this setup
      name_only: only return name of target directory
      package_path: package path of calling test module to be added
                    to conda.pth
    """
    if disable:
        return None
    if shutil.which("conda") is None:
        raise Exception("The 'conda' command is not available in $PATH")
    try:
        version = sp.check_output(["conda", "--version"],
                                  stderr=sp.STDOUT).decode().split()[1]
        if StrictVersion(version) < StrictVersion("4.2"):
            raise Exception(
                "Conda must be version 4.2 or later."
            )
    except sp.CalledProcessError as e:
        raise Exception(
            "Unable to check conda version:\n" + e.output.decode()
        )

    md5hash = hashlib.md5()
    md5hash.update(__file__.encode('utf-8'))
    for env_file in envlist:
        with open(env_file, 'rb') as f:
            md5hash.update(f.read())

    env_path = os.path.join(install_dir, "_".join(
        [name, md5hash.hexdigest()[:8]]))
    if name_only:
        return env_path
    if len(envlist) == 0:
        return None
    # Merge yaml files
    env = {'channels': [], 'dependencies': []}
    for f in envlist:
        with open(f, "r") as fh:
            d = yaml.load(fh)
            env['channels'] = list(set(env['channels'] + d['channels']))
            env['dependencies'] = list(set(env['dependencies'] +
                                           d['dependencies']))
    env_file = os.path.join(env_path, "environment.yaml")
    if not os.path.exists(env_path):
        logger.info("Creating persistent test conda environment for '{}' in '{}'".format(name, env_path))
        logger.info("   (you can modify the location via command line argument '--conda-install-dir';")
        logger.info("    note that this path must be shorter than 80 characters due to issues with some conda builds")
        logger.info("    see e.g. https://github.com/conda/conda-build/issues/1484)")
        logger.info("")
        logger.info("Installing dependencies {}".format(", ".join(env['dependencies'])))
        os.makedirs(env_path)
        conda_args = ["env", "create", "--file", env_file,
                      "--prefix", env_path]
    elif pytest.config.option.conda_update:
        deps = [re.sub("[>=]+.*$", "", x) for x in env['dependencies']]
        logger.info("Updating persistent test conda environment for '{}' in '{}'".format(name, env_path))
        logger.info("")
        logger.info("Updating dependencies {}".format(", ".join(deps)))
        conda_args = ["update", "--prefix", env_path] + deps
    else:
        return None
    try:
        with open(env_file, "w") as fh:
            fh.write(yaml.dump(env, default_flow_style=False))
        out = sp.check_output(["conda"] + conda_args + ["--debug"],
                              stderr=sp.STDOUT)
        logger.info("Environment '{}' created.".format(name))
        if name == "python3":
            try:
                logger.info("Setting up test package '{}' in conda.pth in '{}'".format(package_path, env_path))
                site_packages = glob.glob(os.path.join(
                    env_path, "lib", "python*", "site-packages"))[0]
                conda_pth = os.path.join(site_packages, "conda.pth")
                if package_path is not None:
                    with open(conda_pth, "w") as fh:
                        fh.write(os.path.normpath(package_path))
            except sp.CalledProcessError as e:
                shutil.rmtree(env_path, ignore_errors=True)
                raise Exception(
                    "Could not write conda.pth:\n" +
                    e.output.decode())
    except sp.CalledProcessError as e:
        # remove potential partially installed environment
        shutil.rmtree(env_path, ignore_errors=True)
        raise Exception(
            "Could not create conda environment '{}':\n".format(name) +
            e.output.decode())

    return env_path


@pytest.fixture(autouse=False, scope="session")
def conda_environments(request):
    """Fixture for conda environments"""
    package_path = None
    try:
        fspath = os.path.splitext(str(request._parent_request.fspath))[0]
        m = request._parent_request.module.__name__.replace(".", os.sep)
        package_path = fspath.replace(m, "")
    except:
        logger.warn("evaluation of test package path failed for {}".format(request._parent_request.module.__name__))
    disable = True
    if pytest.config.option.enable_test_conda:
        logger.debug("enabling conda environment setup due to passed --enable-test-conda option")
        disable = False
    if not disable and pytest.config.option.use_conda:
        logger.debug("conda environment setup skipped due to passed --use-conda option")
        disable = True
    if disable:
        return None
    for name, path, envlist in pytest.conda_env_list:
        conda_create_env(name, envlist,
                         install_dir=pytest.config.option.conda_install_dir,
                         package_path=package_path)
