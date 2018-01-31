#!/usr/bin/python

import os

try:
    from setuptools import setup, Extension
except ImportError:
    print "WARNING: SetupTools Error, Falling back to DistUtils"
    from distutils.core import setup, Extension


arm_thumb_dir =  'M-ulator/simulator/core/isa/arm-thumb/' 
arm_thumb_files = map(lambda y: arm_thumb_dir+y, 
                    filter(lambda x: x.endswith('.c'), os.listdir(arm_thumb_dir)))
operations_dir = 'M-ulator/simulator/core/operations/'
operations_files = map(lambda y: operations_dir+y, 
                    filter(lambda x: '.c' in x, os.listdir(operations_dir))) 

# the c extension module
extension_mod = Extension(
    name = "PyMulator.PyMulatorC", 
    define_macros = [ ('M_PROFILE', None), ('NO_PIPELINE', None), \
                        ('DEBUG1', None), ('DEBUG2',None)  ],
    include_dirs = ['M-ulator/simulator/', ],

    sources = [   
        "PyMulator/PyMulatorC/PyMulatorC.c",

        "PyMulator/PyMulatorC/csrc/core.c",
        "PyMulator/PyMulatorC/csrc/extra.c",
        "PyMulator/PyMulatorC/csrc/exception.c",
        "PyMulator/PyMulatorC/csrc/helpers.c",
        "PyMulator/PyMulatorC/csrc/interface.c",
        "PyMulator/PyMulatorC/csrc/interrupts.c",
        "PyMulator/PyMulatorC/csrc/memory.c",
        "PyMulator/PyMulatorC/csrc/registers.c",
        "PyMulator/PyMulatorC/csrc/terminate.c",
        "PyMulator/PyMulatorC/csrc/error.c",

		"M-ulator/simulator/core/isa/decode_helpers.c",
		"M-ulator/simulator/core/isa/decompile.c",
		"M-ulator/simulator/core/opcodes.c",
        "M-ulator/simulator/core/pipeline.c",
		"M-ulator/simulator/cpu/misc.c",

        ] + arm_thumb_files + operations_files,
        #debug only?
        extra_compile_args = ["-std=c11", "-UNDEBUG", "-g", ]
)


from PyMulator import __version__

setup(
    name = "PyMulator", 
    version = __version__,
    author = 'Andrew Lukefahr',
    url = 'https://github.com/lukefahr/PyMulator',

    description = 'Library with a GDB-like interface for Mulator',
    packages= { 'PyMulator',}, 
    #ext_package='PyMulator.PyMulatorC',
    ext_modules=[extension_mod],

    )

