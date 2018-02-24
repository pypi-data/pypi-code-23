"""

keyup :  Copyright 2017-2018, Blake Huber

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

see: https://www.gnu.org/licenses/#GPL

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
contained in the program LICENSE file.

"""

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call
from codecs import open
import keyup


requires = [
    'boto3',
    'botocore',
    'docutils',
    'jmespath',
    'PyYAML',
    'Pygments',
    'pytz',
    's3transfer',
    'six',
    'tqdm'
]


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


class PostInstallDevelop(develop):
    """ post-install, development """
    def run(self):
        check_call("bash scripts/post-install-dev.sh".split())
        develop.run(self)


class PostInstall(install):
    """
    Post-install, production
        cmdclass={
            'develop': PostInstallDevelop,
            'install': PostInstall,
        }
    """
    def run(self):
        check_call("bash post-install.sh".split())
        install.run(self)


setup(
    name='keyup',
    version=keyup.__version__,
    description='Automated IAM Access Key Rotation for Amazon Web Services',
    long_description=read('DESCRIPTION.rst'),
    url='http://keyup.readthedocs.io',
    author=keyup.__author__,
    author_email=keyup.__email__,
    license='GPL-3.0',
    classifiers=[
        'Topic :: Security',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows'
    ],
    keywords='Amazon Web Services iam credentials AWS access key secret key',
    packages=find_packages(exclude=['docs', 'scripts', 'assets']),
    install_requires=requires,
    python_requires='>=3.4, <4',
    entry_points={
        'console_scripts': [
            'keyup=keyup.cli:init_cli',
            'keyconfig=keyup.cli:option_configure'
        ]
    },
    zip_safe=False
)
