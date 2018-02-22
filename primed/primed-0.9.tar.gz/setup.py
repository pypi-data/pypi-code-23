#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  MMMMMMMMMNh  MMMMMMMMMNd  MMMM  MMMMm     MMMM  MMMMMMMMd  MMMMMMMMMN
  MMMMdhhMMMM  MMMMdhhMMMM  MMMM  MMMMMs   /MMMM  MMMMNmmmm  MMMMdhhMMMM
  MMMM   mMMM  MMMM   MMMM  MMMM  MMMMMM-.mMMMMM  MMMM       MMMM   MMMM
  MMMM   mMMM  MMMM   MMMM  MMMM  MMMMMMdsMMMMMM  MMMM       MMMM   MMMM
  MMMM   mMMM  MMMM   MMMM  MMMM  MMMMMMMMMMMMMM  MMMMNddd   MMMM   MMMM
  MMMM   mMMM  MMMMmdmMMMM  MMMM  MMMMdMMMMdMMMM  MMMMNddd   MMMM   MMMM
  MMMM   mMMM  MMMMdMMMMm   MMMM  MMMM/hMMN-MMMM  MMMM       MMMM   MMMM
  MMMM --NMMM  MMMM/ MMMm   MMMM  MMMM  NM  MMMM  MMMM       MMMM   MMMM
  MMMMNNNMMMM  MMMM  dMMM   MMMM  MMMM      MMMM  MMMMMNNNN  MMMMNNNMMMM
  MMMMdhhhhh   hhhh   hhhh  hhhh  hhhh      hhhh  hhhhhhhhs  hhhhhhhhhh
  MMMM
  MMMM
  MMMM
  MMMM
  KP:

########################################################################
#                                                                      #
#                            PRIMED TOOLKIT                            #
#                                                                      #
########################################################################
'''

__author__ = "Eugene Bann, Primed"
__copyright__ = 'Copyright (C) 2018 Demios, Inc.'
__version__ = '0.9'

from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(name                  = 'primed',
      version               = '0.9',
      description           = 'The Primed Toolkit',
      author                = 'Eugene Bann, Primed',
      author_email          = 'eugene@primed.one',
      url                   = 'https://github.com/eyb1/primed',
      python_requires       = '>=3.4',
      license               = 'Apache 2',
      packages              = ['primed', 'primed.data'],
      setup_requires        = ['pytest-runner'],
      tests_require         = ['pytest'],
      install_requires      = ['cython'],
      ext_modules           = [Extension("cnlp", ["cnlp.c"])],
      cmdclass              = {'build_ext': build_ext},
      zip_safe              = False,
      include_package_data  = True
)
