#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import io
from shutil import rmtree

from setuptools import find_packages, setup, Command

here = os.path.abspath(os.path.dirname(__file__))

__version__ = ''
with open(os.path.join('dpic', '__version__.py')) as f:
    exec (f.read())


class PublishCommand(Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except (OSError, IOError):
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


class TestCommand(Command):
    description = 'Run Unit tests.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.status('Testing with pytest...')
        os.system('python -m pytest --cov=dpic tests -v')


# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='data-pack-importer-compare',
    version=__version__,
    description='Command-line validation for datapack import',
    author='David Huser',
    author_email='dhuser@baosystems.com',
    url='https://github.com/davidhuser/data-pack-importer-compare',
    keywords='datim',
    license='BSD3',
    entry_points={
        'console_scripts': [
            'dpi-compare = dpi.compare:main'
        ]
    },
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages(exclude=['tests']),
    cmdclass={
        'publish': PublishCommand,
        'test': TestCommand
    },
)