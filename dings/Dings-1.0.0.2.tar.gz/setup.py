#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: untitled/setup.py.py 
@time: 23/02/188 11:44
"""

#!/usr/bin/env python3

import sys
import os
import re
from io import open
from setuptools import setup, find_packages, Command


if sys.version_info < (2, 7) or (3, 0) <= sys.version_info < (3, 5):
    print('Ding requires at least Python 2.7 or 3.5 to run.')
    sys.exit(1)

with open(os.path.join('Ding', '__init__.py'), encoding='utf-8') as f:
    version = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M).group(1)

if not version:
    raise RuntimeError('Cannot find Ding version information.')

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


def get_data_files():
    data_files = [
        ('share/doc/Ding', ['README.md'])
    ]
    return data_files


def get_install_requires():
    requires = ['requests>=2.18.4', 'urllib3>=1.22']
    return requires

class tests(Command):

    user_options = []

    def initialize_option(self):
        pass

    def run(self):
        pass

setup(
    name='Dings',
    version=version,
    description="Ding Ding bot.",
    long_description=long_description,
    author='ysicing',
    author_email='ops.ysicing@gmail.com',
    url='https://code.cloud.ysicing.net/ysicing/Ding',
    license='LGPLv3',
    keywords='Dingbot',
    install_requires=get_install_requires(),
    packages=find_packages(),
    include_package_data=True,
    data_files=get_data_files(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console :: Curses',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    platforms='any'
)