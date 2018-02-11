#!/usr/bin/env python
#from setuptools import setup, Extension
from distutils.core import setup, Extension
import distutils.sysconfig
import numpy.distutils.misc_util
from distutils.spawn import find_executable
import os

# Get the arrayobject.h(numpy) and python.h(python) header file paths:
include_dirs = numpy.distutils.misc_util.get_numpy_include_dirs()
include_dirs.insert(0, distutils.sysconfig.get_python_inc())
## including conda include/ dir if found
### check for conda environment
try:
    conda_include = os.path.join(os.environ['CONDA_PREFIX'], 'include')
    include_dirs.insert(0, conda_include)
except KeyError:
    conda_include = None
### trying conda base path
if conda_include is None:
    conda_path = find_executable('conda')
    if conda_path is not '':
        p = os.path.split(conda_path)[0]
        p = os.path.split(p)[0]
        p = os.path.join(p, 'include')
        include_dirs.insert(0, p)
        
# c module that requires gsl
module1 = Extension('_C_mixextend',
                    ['SIPSim_pymix/C_mixextend.c'],
                    include_dirs = include_dirs,
                    libraries = ['gsl', 'gslcblas' ,'m'])

# setup
setup(name='SIPSim_pymix',
      version="0.1.2",
      description='Python mixture package dependency for SIPSim',
      long_description="See the README",      
      author="Nick Youngblut",
      author_email="nyoungb2@gmail.com",
      url ="https://github.com/nick-youngblut/SIPSim_pymix",
      license='GNU General Public License v2.0',
      packages = ['SIPSim_pymix'],
      package_dir = {'SIPSim_pymix' : 'SIPSim_pymix'},
      ext_modules = [module1],
      requires = ['numpy']
     )
