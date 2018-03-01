"""Setup for the folk package."""

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import warnings
import setuptools
import versioneer


# Require Python 3.4 or higher
if sys.version_info.major < 3 or sys.version_info.minor < 5:
    warnings.warn("folk requires Python 3.5 or higher!")
    sys.exit(1)


INSTALL_REQUIRES = [
    'numpy', 'scipy', 'scikit-learn',
    # my packages
    'birch>=0.0.6', 'decore', 'strct', 'pdutil', 'pymongo',
]
TEST_REQUIRES = [
    # testing and coverage
    'pytest', 'coverage', 'pytest-cov',
    # test dependencies
    'pandas', 'pdpipe', 'skutil',
    # to be able to run `python setup.py checkdocs`
    'collective.checkdocs', 'pygments',
]

with open('README.rst') as f:
    README = f.read()

setuptools.setup(
    author="Shay Palachy",
    author_email="shay.palachy@gmail.com",
    name='folk',
    description='Folksy experiment management for Machine Learning.',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    long_description=README,
    url='https://github.com/shaypal5/folk',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        INSTALL_REQUIRES
    ],
    extras_require={
        'test': TEST_REQUIRES + INSTALL_REQUIRES,
    },
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
)
