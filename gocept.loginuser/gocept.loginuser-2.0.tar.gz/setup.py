# Copyright (c) 2015 gocept gmbh & co. kg
# See also LICENSE.txt

# This should be only one line. If it must be multi-line, indent the second
# line onwards to keep the PKG-INFO file format intact.
"""Sqlalchemy user object and password management.
"""

from setuptools import setup, find_packages
import glob


setup(
    name='gocept.loginuser',
    version='2.0',
    install_requires=[
        'AuthEncoding >= 4.0',
        'bcrypt',
        'setuptools',
        'six',
        'sqlalchemy',
    ],

    extras_require={
        'test': [
            'gocept.testing',
        ],
    },

    entry_points={
        'console_scripts': [
            # 'binary-name = gocept.loginuser.module:function'
        ],
    },

    author='gocept <mail@gocept.com>',
    author_email='mail@gocept.com',
    license='ZPL 2.1',
    url='https://bitbucket.org/gocept/gocept.loginuser/',

    keywords='Sqlalchemy user password login',
    classifiers="""\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved
Natural Language :: English
Topic :: Database
Topic :: Software Development
Operating System :: OS Independent
License :: OSI Approved :: Zope Public License
Programming Language :: Python :: Implementation
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(name).read() for name in (
        'README.txt',
        'HACKING.txt',
        'CHANGES.txt',
    )),
    namespace_packages=['gocept'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    data_files=[('', glob.glob('*.txt'))],
    zip_safe=False,
)
