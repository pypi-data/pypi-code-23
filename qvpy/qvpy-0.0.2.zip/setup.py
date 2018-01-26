# -*- coding: utf-8 -*-


### imports ###################################################################
import logging
import os

### imports from ##############################################################
from setuptools import find_packages, setup

### variables #################################################################
AUTHOR = 'hirschbeutel'
AUTHOR_EMAIL = 'hirschbeutel@gmail.com'

DESCRIPTION = 'Mitutoyo QVPak COM client'
PACKAGE_NAME = 'qvpy'
URL = 'https://bitbucket.org/hirschbeutel/qvpy'

###############################################################################
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

###############################################################################
setup(
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        license='MIT',
        long_description=read_package_variable(__doc__),
        name=read_package_variable('__project__'),
        packages=find_packages(),
        version=read_package_variable('__version__'),
        url=URL,)
