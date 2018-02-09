#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, Extension
from distutils.command.build_ext import build_ext

# cheap argument parsing
# -L add a library directory
# -I add an include directory
import sys
includes=[]
libs=[]
args=[]
lm=len(sys.argv) - 1
i = 0
while i < len(sys.argv):
    arg=sys.argv[i]
    if arg == '-I' and i < lm:
        includes.append(sys.argv[i+1])
        i += 1
    elif arg == '-L' and i < lm:
        libs.append(sys.argv[i+1])
        i += 1
    else:
        args.append(arg)
    i += 1
sys.argv=args

copt =  {'msvc': ['/EHsc'],
         'unix' : ['-std=c++11'] }
libs_opt =  {'msvc' : ['tempus', 'boost_python-vc140-mt-1_63', 'libpq'],
             'unix' : ['tempus', 'boost_python-py{}{}'.format(sys.version_info.major, sys.version_info.minor)] }


class build_ext_subclass( build_ext ):
    def build_extensions(self):
        c = self.compiler.compiler_type
        if c in copt:
           for e in self.extensions:
               e.extra_compile_args = copt[ c ]
        if c in libs_opt:
            for e in self.extensions:
                e.libraries = libs_opt[ c ]
        build_ext.build_extensions(self)

setup(
    name='pytempus',
    version='1.2.2',
    description="Tempus Python API",
    long_description="Tempus Python API module",
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: System :: Software Distribution",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    keywords='',
    author='Tempus Team',
    author_email='infos@oslandia.com',
    maintainer='Oslandia',
    maintainer_email='infos@oslandia.com',

    license='LGPL',
    packages=['tempus'],
    ext_modules=[Extension('pytempus',
                           include_dirs = includes,
                           library_dirs = libs,
                           sources = ['src/pytempus.cc',
                                      'src/cost.cc',
                                      'src/multimodal_graph.cc',
                                      'src/plugin.cc',
                                      'src/plugin_factory.cc',
                                      'src/poi.cc',
                                      'src/point.cc',
                                      'src/progression.cc',
                                      'src/public_transport.cc',
                                      'src/request.cc',
                                      'src/road_graph.cc',
                                      'src/roadmap.cc',
                                      'src/routing_data.cc',
                                      'src/transport_mode.cc',
                                      'src/variant.cc'])],
    cmdclass = {'build_ext': build_ext_subclass },
    include_package_data=True,
    zip_safe=False,
    install_requires=(),
    extras_require={
        "develop": ()
    }
)
