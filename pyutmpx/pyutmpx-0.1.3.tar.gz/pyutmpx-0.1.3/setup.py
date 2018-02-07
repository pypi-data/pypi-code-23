#!/usr/bin/env python3
#******************************************************************************
# Copyright (C) 2017-2018 Thomas "Cakeisalie5" Touhey <thomas@touhey.fr>
# This file is part of the pyutmpx Python 3.x module, which is MIT-licensed.
#******************************************************************************
""" Setup script for the utmpx module. """

import os, subprocess
from setuptools import setup, Extension

# Find the sources
srcdir = "src"
incdir = "include"

src = os.listdir(srcdir)
src = filter(lambda x: x.split('.')[-1] in ("c",), src)
src = map(lambda x: os.path.join(srcdir, x), src)
src = list(src)

# Make the setup
setup(
	name="pyutmpx",
	version="0.1.3",
	url="https://forge.touhey.fr/pyutmpx.git/",
	license='MIT',
	keywords='utmp utmpx',
	description="utmp reader module for Python 3.x",
	author='Thomas "Cakeisalie5" Touhey',
	author_email='thomas@touhey.fr',

	ext_modules=[Extension("pyutmpx", src,
		include_dirs=[incdir], library_dirs=[], libraries=[])],

	classifiers = [
		'License :: OSI Approved :: MIT License',
	]
)

# End of file.
