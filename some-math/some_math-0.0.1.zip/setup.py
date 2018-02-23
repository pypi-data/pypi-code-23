# -*- coding: utf-8 -*-

import logging
import os

from setuptools import find_packages, setup

AUTHOR = 'hirschbeutel'
AUTHOR_EMAIL = 'hirschbeutel@gmail.com'

DESCRIPTION = 'some math routines'
LONG_DESCRIPTION = 'some math routines'
PACKAGE_NAME = 'some_math'
URL = 'https://bitbucket.org/hirschbeutel/some_math'


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
        description=DESCRIPTION,
        license='MIT',
        long_description=LONG_DESCRIPTION,
        name=read_package_variable('__project__'),
        packages=find_packages(),
        version=read_package_variable('__version__'),
        url=URL,)

