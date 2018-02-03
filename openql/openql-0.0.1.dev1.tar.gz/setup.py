#!/usr/bin/env python

from os import path

dir_setup = path.dirname(path.realpath(__file__))
requires = [];

from setuptools import setup, Command

modules = [
    ]

tests = [
    ]

long_description = '''OpenQL is the Quantum library in Python
It provides Quantum Computer Emulator and various open source libraries for using quantum computing.'''

with open(path.join(dir_setup, 'openql', 'release.py')) as f:
    # Defines __version__
    exec(f.read())


if __name__ == '__main__':
    setup(name='openql',
        version=__version__,
        description='OpenQL is the Quantum library in Python.',
        long_description=long_description,
        author='OpenQL development team',
        author_email='committer@openql.org',
        license='Apache 2.0',
        keywords="Math Physics quantum",
        url='http://openql.org',
        packages=['openql'] + modules + tests,
        ext_modules=[],
        classifiers=[
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Physics',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            ],
        install_requires=requires,
        )
