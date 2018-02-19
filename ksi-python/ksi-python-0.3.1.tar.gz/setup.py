#####################################################################
# Copyright (C) 2015-18 Guardtime, Inc
# This file is part of the Guardtime client SDK.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES, CONDITIONS, OR OTHER LICENSES OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
# "Guardtime" and "KSI" are trademarks or registered trademarks of
# Guardtime, Inc., and no license to trademarks is granted; Guardtime
# reserves and retains all trademark rights.

import os
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

long_description = ""
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst')) as f:
    long_description = f.read()

KSI_WRAPPER = Extension('_ksi',
                        sources=['_ksi.c'],
                        libraries=['ksi', 'crypto', 'curl']
                       )

setup(name='ksi-python',
      description="""Python wrapper for libksi, a library for accessing Guardtime KSI service""",
      long_description=long_description,
      version='0.3.1',
      url="https://github.com/guardtime/ksi-python",
      author="Guardtime",
      author_email="info@guardtime.com",
      license="Apache 2.0",
      platforms=["any"],
      ext_modules=[KSI_WRAPPER],
      py_modules=["ksi"],
      test_suite="tests"
     )
