"""
Copyright 2017 Gu Zhengxiong <rectigu@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import os

from setuptools import setup, find_packages


PROGRAM_NAME = 'PyCliProg'
PACKAGE_NAME = PROGRAM_NAME.lower()


__author__ = 'Gu Zhengxiong'

_my_dir = os.path.dirname(__file__)
VERSION_FILE = 'VERSION.txt'
_version_path = os.path.join(_my_dir, PACKAGE_NAME, VERSION_FILE)
with open(_version_path) as stream:
    __version__ = stream.read().strip()


setup(
    name=PROGRAM_NAME,
    author=__author__,
    author_email='rectigu@gmail.com',
    version=__version__,
    description='A minimal-complete Python command-line program.',
    license='Apache License Version 2.0',
    keywords='command-line program',
    url='https://gitlab.com/imtheforce/{}'.format(PACKAGE_NAME),
    packages=find_packages(),
    package_data={
        PACKAGE_NAME: [VERSION_FILE]
    }
)
