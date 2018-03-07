# Copyright (C) 2018 DataArt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================


import os
import re
from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


def get_version(package):
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('devicehive_plugin')


setup(name='devicehive_plugin',
      version=version,
      author='DataArt (http://dataart.com)',
      author_email='info@devicehive.com',
      url='https://devicehive.com',
      license='Apache License 2.0',
      description='DeviceHive Python plugin connectivity library',
      long_description=long_description,
      keywords='iot cloud m2m gateway embedded devicehive plugin',
      packages=['devicehive_plugin'],
      install_requires=['websocket-client>=0.47.0', 'requests>=2.18.4',
                        'six>=1.11.0'],
      python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Home Automation',
          'Topic :: Internet',
          'Topic :: Software Development :: Embedded Systems',
      ])
