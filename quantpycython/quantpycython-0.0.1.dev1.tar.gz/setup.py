#!/usr/bin/env python

from os import path

dir_setup = path.dirname(path.realpath(__file__))
requires = [];

from setuptools import setup, Command

modules = [
    ]

tests = [
    ]

long_description = '''QuantPyCython is the QuantPy library Plugin using Cython for quantum computing.
It aims to become extension library set of quantpy.'''

with open(path.join(dir_setup, 'quantpycython', 'release.py')) as f:
    # Defines __version__
    exec(f.read())


if __name__ == '__main__':
    setup(name='quantpycython',
        version=__version__,
        description='QuantPy Plugin using Cython, that extends quantum Executor/Simulator.',
        long_description=long_description,
        author='QuantPy development team',
        author_email='quantpy@openql.org',
        license='Apache 2.0',
        keywords="Math Physics quantum quantpy",
        url='http://quantpy.org',
        packages=['quantpycython'] + modules + tests,
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
