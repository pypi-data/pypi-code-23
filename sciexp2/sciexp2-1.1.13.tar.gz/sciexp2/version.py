#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SciExp² version information."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2013-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


__version_info__ = (1, 1, 13)
__version__ = ".".join([str(i) for i in __version_info__])


CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering",
]


_description = "Scientific Experiment Exploration framework"

# taken from doc/introduction.rst
_long_description = """\
SciExp² (aka *SciExp square* or simply *SciExp2*) stands for *Scientific
Experiment Exploration*, which provides a framework for easing the workflow of
creating, executing and evaluating experiments.

The driving idea of SciExp² is that of quick and effortless *design-space
exploration*. It is divided into the following main pieces:

- Launchgen: Aids in defining experiments as a permutation of different
  parameters in the design space. It creates the necessary files to run these
  experiments (configuration files, scripts, etc.), which you define as
  templates that get substituted with the specific parameter values of each
  experiment.

- Launcher: Takes the files of launchgen and runs these experiments on different
  execution platforms like regular local scripts or cluster jobs. It takes care
  of tracking their correct execution, and allows selecting which experiments to
  run (e.g., those with specific parameter values, or those that were not
  successfully run yet).

- Data: Aids in the process of collecting and analyzing the results of the
  experiments. Results are automatically collected into a data structure that
  maintains the relationship between each result and the parameters of the
  experiment that produced it. With this you can effortlessly perform complex
  tasks such as inspecting the results or calculating statistics of experiment
  sub-sets, based on their parameter values.
"""


NAME = "sciexp2"
VERSION = __version__
DESCRIPTION = _description
LONG_DESCRIPTION = _long_description
AUTHOR = __author__
AUTHOR_EMAIL = __email__
MAINTAINER = __maintainer__
MAINTAINER_EMAIL = __email__
URL = "https://projects.gso.ac.upc.edu/projects/sciexp2"
LICENSE = "GNU General Public License (GPL) version 3 or later"
PACKAGES = ["sciexp2", "sciexp2.common", "sciexp2.launchgen", "sciexp2.system",
            "sciexp2.data", "sciexp2.data.io"]
PACKAGE_DATA = {"sciexp2": ["templates/*.dsc", "templates/*.tpl"]}
SCRIPTS = ["launcher"]
REQUIRES = ["numpy", "ply", "ipython", "six", "tqdm"]
PROVIDES = ["sciexp2"]

INSTALL_REQUIRES = [req.replace("(", "").replace(")", "") for req in REQUIRES]
