#!/usr/bin/env python
# VisiLibity: a Python binding of VisiLibity1
# Copyright (C) 2018 Yu Cao < University of Southampton> Yu.Cao at soton.ac.uk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or 
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA

from distutils.core import setup, Extension
from distutils.command.build import build

class CustomBuild(build):
    sub_commands = [
        ('build_ext',     build.has_ext_modules),
        ('build_py',      build.has_pure_modules),
        ('build_clib',    build.has_c_libraries),
        ('build_scripts', build.has_scripts),
                    ]

module = Extension('_visilibity', swig_opts = ['-c++'],
        sources = ['visilibity.i', 'visilibity.cpp'],
        headers = ['visilibity.hpp'], include = ['visilibity.hpp'])

setup (name = 'VisiLibity',
       version = '1.0.7',
       cmdclass = {'build': CustomBuild},
       author = 'Yu Cao',
       author_email = 'yu.cao@soton.ac.uk',
       url = 'https://github.com/tsaoyu/VisiLibity1',
       description = 'Python bindings of VisiLibity1',
       py_modules = ['visilibity'],
       ext_modules = [module])
