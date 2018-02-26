# Copyright 2017 NEWCRAFT GROUP B.V.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from setuptools import find_packages
from setuptools import setup

options = {
    "name": "nci-python-commands",
    "version": "1.0.8",
    "description": "An object orientated CLI command library",
    "url": "https://github.com/newcraftgroup/nci-python-commands",
    "author": 'NEWCRAFT',
    "author_email": 'job.tiel.groenestege@newcraftgroup.com',
    "license": 'Apache License, Version 2.0',
    "classifiers": [
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    "keywords": 'development command commandtool terminal cli',
    "packages": find_packages(exclude=['docs', 'tests*']),
    "scripts": ['bin/manage'],
    "install_requires": [
        "nci-config-loader==1.0.12"
    ]
}

setup(**options)
