# Copyright (C) 2016-2018 Barry A. Warsaw
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setup_helpers import get_version, require_python
from setuptools import setup


require_python(0x030400f0)
__version__ = get_version('flufl/flake8/__init__.py')


setup(
    name='flufl.flake8',
    version=__version__,
    namespace_packages=['flufl'],
    packages=['flufl.flake8'],
    include_package_data=True,
    maintainer='Barry Warsaw',
    maintainer_email='barry@python.org',
    description='A flake8 plugin for GNU Mailman import order',
    license='ASLv2',
    url='https://gitlab.com/warsaw/flufl.flake8',
    download_url='https://pypi.python.org/pypi/flufl.flake8',
    entry_points={
        'flake8.extension': ['U4 = flufl.flake8.imports:ImportOrder'],
        },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        ]
    )
