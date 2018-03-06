#!/usr/bin/env python
# encoding: utf8

from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

def readme():
    "Falls back to just file().read() on any error, because the conversion to rst is only really relevant when uploading the package to pypi"
    from subprocess import CalledProcessError
    try:
        from subprocess import check_output
        return str(check_output(['pandoc', '--from', 'markdown', '--to', 'rst', 'README.md']))
    except (ImportError, OSError, CalledProcessError) as error:
        print('python2.7 and pandoc is required to get the description as rst (as required to get nice rendering in pypi) - using the original markdown instead.',
              'See http://johnmacfarlane.net/pandoc/')
    return str(open(path.join(here, 'README.md')).read())


tests_require=[
    'PythonicTestcase',
],

setup(
    name='valueobject',
    version='1.0.1',
    description='ValueObject is a dict-like object that exposes keys as attributes.',
    long_description=readme(),
    author='Felix Schwarz, Martin Häcker, Robert Buchholz',
    author_email='rbu@goodpoint.de, spamfaenger@gmx.de',
    license='ISC',
    url='https://github.com/rbu/valueobject',
    packages=find_packages(),
    test_suite="valueobject",
    tests_require=tests_require,
    extras_require = dict(
        testing=tests_require,
    ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)
