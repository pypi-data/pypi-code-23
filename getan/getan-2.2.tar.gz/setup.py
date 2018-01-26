#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2011, 2014 by Björn Ricks <bjoern.ricks@intevation.de>
# (c) 2017 by Intevation GmbH
#
# Author(s):
#  * Björn Ricks <bjoern.ricks@intevation.de>
#  * Bernhard Reiter <bernhard.reiter@intevation.de>
#
# A python worklog-alike to log what you have 'getan' (done).
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import glob
import os.path

from setuptools import setup, find_packages

import getan

cur_dir = os.path.dirname(__file__)
scripts_dir = os.path.join(cur_dir, "scripts")


def read(fname):
    with open(os.path.join(cur_dir, fname)) as f:
        return f.read()

setup(name="getan",
      version=getan.__version__,
      description="Terminal based time-tracking "
                  "and reporting tool; comparable to 'worklog'.",
      url="https://getan.wald.intevation.org/",
      download_url="https://scm.wald.intevation.org/hg/getan/",
      maintainer="Bernhard E. Reiter",
      maintainer_email="bernhard.reiter@intevation.de",
      license="GPLv3+",
      long_description=read("README"),
      packages=find_packages(),
      package_data={
          "": ["*.txt"],
          "getan": ["templates/*"],
      },
      install_requires=[
          'jinja2',
          'urwid>=1.1.2'
      ],
      scripts=glob.glob(os.path.join(scripts_dir, "*.py")) +
      [os.path.join(scripts_dir, "wochenbericht"),
       os.path.join(scripts_dir, "convert-projects")],
      entry_points={"console_scripts":
                    ["getan=getan.main:main",
                     "getan-classic=getan.classic.getan:main",
                     ]},
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Topic :: Utilities",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: "
              "GNU General Public License v3 or later (GPLv3+)",
          "Operating System :: POSIX",
          "Programming Language :: Python :: 2"
      ],
      )
