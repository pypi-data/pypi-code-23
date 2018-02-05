#/*-----------------------------------------------------------------*/
#/*! 
#  \file setup.py 
#  \brief Python installer for calceph library
#
#  \author  M. Gastineau 
#           Astronomie et Systemes Dynamiques, IMCCE, CNRS, Observatoire de Paris. 
#
#   Copyright, 2016,2017, CNRS
#   email of the author : Mickael.Gastineau@obspm.fr
#*/
#/*-----------------------------------------------------------------*/
# 
#/*-----------------------------------------------------------------*/
#/* License  of this file :
# This file is "triple-licensed", you have to choose one  of the three licenses 
# below to apply on this file.
# 
#    CeCILL-C
#    	The CeCILL-C license is close to the GNU LGPL.
#    	( http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html )
#   
# or CeCILL-B
#        The CeCILL-B license is close to the BSD.
#        (http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.txt)
#  
# or CeCILL v2.1
#      The CeCILL license is compatible with the GNU GPL.
#      ( http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html )
# 
#
# This library is governed by the CeCILL-C, CeCILL-B or the CeCILL license under 
# French law and abiding by the rules of distribution of free software.  
# You can  use, modify and/ or redistribute the software under the terms 
# of the CeCILL-C,CeCILL-B or CeCILL license as circulated by CEA, CNRS and INRIA  
# at the following URL "http://www.cecill.info". 
# 
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 
# 
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 
# 
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-C,CeCILL-B or CeCILL license and that you accept its terms.
# */
# /*-----------------------------------------------------------------*/

# see http://docs.cython.org/en/latest/src/tutorial/clibraries.html
# require to install Cython.Distutils
#  pip install Cython
# execute  : python setup.py sdist

from distutils.core import setup
from distutils.extension import Extension
from distutils.command.install import install
from distutils.command.build import build
from distutils.command.build_clib import build_clib
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_config_var, get_config_vars
from distutils import log
from subprocess import  check_call
from Cython.Distutils import build_ext
import os
import shutil
import sys

class custom_build_ext(build_ext):
    def run(self):
        self.run_command('build_clib')
        build_ext.run(self)

class custom_build_clib(build_clib):
    def run(self):
        cc, cflags = get_config_vars('CC','CFLAGS')
        if os.system("chmod 0755 configure") != 0:
            raise RuntimeError("chmod error")
        # Destination for headers and libraries is build_clib.
        build_clib = os.path.realpath(self.build_clib)
        env = dict(os.environ)
        cflags = cflags+ ' '+'-Isrc'
        cmd = ['/bin/sh', './configure',
                '--prefix=' + build_clib,
                '--enable-shared',
                '--disable-static',
                '--enable-fortran=no',
                '--enable-python',
                '--prefix=' + build_clib] 
        log.info('%s', ' '.join(cmd))
        check_call(cmd, env=dict(env, CC=cc, CFLAGS=cflags))           
        check_call(['make', 'clean'], env=env)           
        check_call(['make'], env=env)           
        check_call(['make', 'check'], env=env)           
 
setup(
    name='calcephpy',
    version='3.0.0',
    description='Python interface for the CALCEPH Library',
    author='Mickael Gastineau',
    author_email='inpop.imcce@obspm.fr',
    url='http://www.imcce.fr/inpop/calceph/',
    license='CeCILL-C or CeCILL-B or CeCILL v2.1',
    classifiers=[ 'Topic :: Scientific/Engineering :: Astronomy', 'Topic :: Software Development :: Libraries' ],
    cmdclass = {'build_ext':  custom_build_ext, 'build_clib':  custom_build_clib},
    ext_modules = [
        Extension("calcephpy", ["pythonapi/src/calcephpy.pyx"],
              include_dirs = ["src"], 
              library_dirs = ["src/.libs"],
              libraries=["calcephnoinst"])
    ],
    install_requires=['cython']
)
