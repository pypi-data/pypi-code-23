# -*- coding: utf-8 -*-

import logging
import os

from setuptools import setup

AUTHOR = 'hirschbeutel'
AUTHOR_EMAIL = 'hirschbeutel@gmail.com'

CLASSIFIERS = [
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics']

DESCRIPTION = 'Bruker Opus FTIR spectroscopy clone'
LONG_DESCRIPTION = 'Bruker Opus FTIR spectroscopy clone'
PACKAGE_NAME = 'ono'
URL = 'https://bitbucket.org/hirschbeutel/ono'


def read_package_variable(key, filename='__init__.py'):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, filename)

    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ', 2)

            if parts[:-1] == [key, '=']:
                return parts[-1].strip("'")

    logging.warning("'%s' not found in '%s'", key, module_path)
    return None


setup(
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
	classifiers=CLASSIFIERS,
        description=DESCRIPTION,
        license='MIT',
        long_description=LONG_DESCRIPTION,
        name=read_package_variable('__project__'),
        packages=[PACKAGE_NAME],
        version=read_package_variable('__version__'),
        url=URL,)

