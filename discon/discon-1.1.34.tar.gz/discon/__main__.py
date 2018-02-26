#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © %YEAR%  <>
#
# Distributed under terms of the %LICENSE% license.

"""
Push project to pypi and binstar (Anaconda)


"""

import logging

logger = logging.getLogger(__name__)
import argparse
import subprocess
import os
import os.path as op
import shutil
import glob
import git


def mycall(command):
    if type(command) is list:
        subprocess.call(command)
    else:
        subprocess.call(command, shell=True)


def make(args):
    if not op.exists("build.sh"):
        with open('build.sh', 'a') as the_file:
            the_file.write('#!/bin/bash\n\n$PYTHON setup.py install\n')
    if not op.exists("bld.bat"):
        with open('bld.bat', 'a') as the_file:
            the_file.write('"%PYTHON%" setup.py install\nif errorlevel 1 exit 1')

    repo = git.Repo(".")
    if repo.is_dirty():
        logger.error("Git working directory is dirty. Clean it.")
        return
    if (args.action == "init"):
        init(args.initprojectname)
        return
    elif (args.action == "stable"):
        mycall("git push --tags")
        mycall("git checkout stable")
        mycall("git pull origin master")
        mycall("git push")
        mycall("git checkout master")
        return
    elif args.action in ["minor", "major", "patch"]:
        logger.debug("pull, patch, push, push --tags")
        mycall("git pull")
        mycall("bumpversion " + args.action)
        mycall("git push")
        mycall("git push --tags")
    elif args.action in ["upload"]:
        logger.debug("just upload to conda and pypi")
    else:
        logger.error("Unkown command '"+ args.action + "'")
        return
# fi
    # upload to pypi
    pypi_build_and_upload(args)


    pythons = args.py
    if len(args.py) == 0 or (len(args.py) > 0 and args.py in ("both", "all")):
        pythons = ["2.7", "3.6"]
    logger.debug("python versions " + str( args.py))

    for python_version in pythons:
        conda_build_and_upload(python_version, args.channel)

def pypi_build_and_upload(args):
    pypi_upload = True
    if not args.no_pypi:
        pypi_upload = False

    if pypi_upload:
        logger.debug("pypi upload")
        # preregistration is no longer required
        # mycall(["python", "setup.py", "register", "-r", "pypi"])
        mycall(["python", "setup.py", "sdist", "upload", "-r", "pypi"])

    # build conda and upload
    logger.debug("conda clean")

    dr = glob.glob("win-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("linux-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("osx-*")
    for onedir in dr:
        shutil.rmtree(onedir)

    # this fixes upload confilct
    dr = glob.glob("dist/*.tar.gz")
    for onefile in dr:
        os.remove(onefile)



def conda_build_and_upload(python_version, channels):

    logger.debug("conda build")
    logger.debug("build python_version :" + str( python_version))

    # subprocess.call("conda build -c mjirik -c SimpleITK .", shell=True)
    conda_build_command = ["conda", "build", "--py", python_version,  "."]
    for channel in channels:
        conda_build_command.append("-c")
        conda_build_command.append(channel[0])

    mycall(conda_build_command)
    conda_build_command.append("--output")
    # output_name_lines = subprocess.check_output(["conda", "build", "--python", python_version, "--output", "."])
    logger.debug(" ".join(conda_build_command))
    output_name_lines = subprocess.check_output(conda_build_command)
    # get last line of output
    output_name = output_name_lines.split("\n")[-2]
    logger.debug("build output file: " + output_name)
    cmd_convert = ["conda", "convert", "-p", "all", output_name]
    logger.debug(" ".join(cmd_convert))
    mycall(cmd_convert)

    logger.debug("binstar upload")
    # it could be ".tar.gz" or ".tar.bz2"
    mycall(["anaconda", "upload", output_name])
    mycall("anaconda upload */*.tar.*z*")

    logger.debug("rm files")
    dr = glob.glob("win-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("linux-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("osx-*")
    for onedir in dr:
        shutil.rmtree(onedir)

def init(project_name="project_name"):
    _SETUP_PY = """# Fallowing command is used to upload to pipy
#    python setup.py register sdist upload
from setuptools import setup, find_packages
# Always prefer setuptools over distutils
from os import path

here = path.abspath(path.dirname(__file__))
setup(
    name='{name}',
    description='{description}',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.0',
    url='https://github.com/mjirik/{}',
    author='Miroslav Jirik',
    author_email='miroslav.jirik@gmail.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='{keywords}',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['dist',  'docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=['numpy', 'conda'],
    # 'SimpleITK'],  # Removed becaouse of errors when pip is installing
    dependency_links=[],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={{
    #     'sample': ['package_data.dat'],
    # }},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={{
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # }},
)
"""

    _SETUP_CFG = """
[bumpversion]
current_version = 0.0.0
files = setup.py meta.yaml
commit = True
tag = True
tag_name = {new_version}

[nosetests]
attr = !interactive,!slow,!LAR
"""

    _META_YML = """package:
  name: {name}
  version: "0.0.0"

source:
# this is used for build from git hub
  git_rev: 0.0.0
  git_url: https://github.com/mjirik/{name}.git

# this is used for pypi
  # fn: io3d-1.0.30.tar.gz
  # url: https://pypi.python.org/packages/source/i/io3d/io3d-1.0.30.tar.gz
  # md5: a3ce512c4c97ac2410e6dcc96a801bd8
#  patches:
   # List any patch files here
   # - fix.patch

# build:
  # noarch_python: True
  # preserve_egg_dir: True
  # entry_points:
    # Put any entry points (scripts to be generated automatically) here. The
    # syntax is module:function.  For example
    #
    # - {name} = {name}:main
    #
    # Would create an entry point called io3d that calls {name}.main()


  # If this is a new build for the same version, increment the build
  # number. If you do not include this key, it defaults to 0.
  # number: 1

requirements:
  build:
    - python
    - setuptools

  run:
    - python
    # - numpy
    # - pyqt 4.11.*

test:
  # Python imports
  imports:
    - {name}

  # commands:
    # You can put test commands to be run here.  Use this to test that the
    # entry points work.


  # You can also put a file called run_test.py in the recipe that will be run
  # at test time.

  # requires:
    # Put any additional test requirements here.  For example
    # - nose

about:
  home: https://github.com/mjirik/{name}
  license: BSD License
  summary: 'distribution to pypi and conda'

# See
# http://docs.continuum.io/conda/build.html for
# more information about meta.yaml
"""


    _CONDARC = """#!/bin/bash

$PYTHON setup.py install

# Add more build steps here, if they are necessary.

# See
# http://docs.continuum.io/conda/build.html
# for a list of environment variables that are set during the build process.
"""

    _TRAVIS_YML="""language: python
python:
  #  - "2.6"
  - "2.7"
  # - "3.2"
  # - "3.3"
  # - "3.4"


os: linux
# Ubuntu 14.04 Trusty support
sudo: required
dist: trusty
# install new cmake
#addons:
#  apt:
#    packages:
#      - cmake
#    sources:
#      - kalakris-cmake
virtualenv:
  system_site_packages: true
before_script:
    # GUI
    - "export DISPLAY=:99.0"
    - "sh -e /etc/init.d/xvfb start"
    - sleep 3 # give xvfb sume time to start

before_install:
    - wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
    - chmod +x miniconda.sh
    - ./miniconda.sh -b
    - export PATH=/home/travis/miniconda2/bin:$PATH
    - sudo apt-get update

#    - sudo apt-get install -qq cmake libinsighttoolkit3-dev libpng12-dev libgdcm2-dev
    # - wget http://147.228.240.61/queetech/sample-extra-data/io3d_sample_data.zip && unzip io3d_sample_data.zip
# command to install dependencies
install:

    - conda update --yes conda
    - conda install --yes pip nose coverage
#    - Install dependencies
    - conda install --yes -c SimpleITK -c luispedro -c mjirik --file requirements_conda.txt
#    - pip install -r requirements_pip.txt
#    - "echo $LD_LIBRARY_PATH"
#    - "pip install -r requirements.txt"
#    - 'mkdir build'
#    - "cd build"
#    - "cmake .."
#    - "cmake --build ."
#    - "sudo make install"
#    - pip install .
#    - "cd .."
#    - 'echo "include /usr/local/lib" | sudo tee -a /etc/ld.so.conf'
#    - 'sudo ldconfig -v'
#    - conda list -e
# command to run tests
script: nosetests --with-coverage --cover-package={name}
after_success:
    - coveralls
"""
    if not op.exists(".condarc"):
        with open('.condarc', 'a') as the_file:
            the_file.write('channels:\n  - default\n#  - mjirik')
    if not op.exists("setup.py"):
        with open('setup.py', 'a') as the_file:
            the_file.write(_SETUP_PY.format(name=project_name, description="", keywords=""))
    if not op.exists("setup.cfg"):
        with open('setup.cfg', 'a') as the_file:
            the_file.write(_SETUP_CFG)
    if not op.exists("meta.yaml"):
        with open('meta.yaml', 'a') as the_file:
            the_file.write(_META_YML.format(name=project_name))
    if not op.exists(".travis.yaml"):
        with open('.travis.yaml', 'a') as the_file:
            the_file.write(_TRAVIS_YML.format(name=project_name))


def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "action",
        help="Available values are: 'init', 'patch', 'minor', 'major', 'stable' or 'upload' ",
        default=None)
    parser.add_argument(
        "initprojectname",
        nargs='?',
        help="set project name in generated files if 'init' action is used",
        default="default_project")
    parser.add_argument("--py",
            # default="2.7",
            # default="both",
            action="append",
            default=[],
            # default="all",
            help="specify python version. '--py 2.7' or '--py both' for python 3.6 and 2.7" )
    parser.add_argument(
        "-c", "--channel",
        nargs=1,
        action="append",
        help="Add conda channel",
        default=[])
    # parser.add_argument(
    #     "arg2",
    #     required=False,
    #     default=None)
    # parser.add_argument(
    #     '-i', '--inputfile',
    #     default=None,
    #     # required=True,
    #     help='input file'
    # )
    parser.add_argument(
        '-ll', '--loglevel', type=int, default=None,
        help='Debug level 0 to 100')

    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    parser.add_argument(
        '-np', '--no-pypi', action='store_true',
        help='Do not upload to pypi')
    args = parser.parse_args()

    if args.loglevel is not None:
        ch.setLevel(args.loglevel)

    if args.debug:
        ch.setLevel(logging.DEBUG)

    make(args)


if __name__ == "__main__":
    main()

