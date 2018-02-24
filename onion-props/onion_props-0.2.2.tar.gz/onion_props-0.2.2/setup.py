#!/usr/bin/python3

import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    README = ''
    CHANGES = ''

setup(
    name='onion_props',
    version='0.2.2',
    description='An elegant hierarchical (or "onioned") properties parser',
    long_description=README + '\n\n' + CHANGES,
    url='https://github.com/eternali/onion_props',
    author='Conrad Heidebrecht',
    author_email='conrad.heidebrecht@gmail.com',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='properties java parser',
    py_modules=['onion_props'],
    install_requires=['datetime']
)
