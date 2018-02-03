"""Packaging setting"""

from os.path import abspath, dirname, join
from subprocess import call

from setuptools import setup, find_packages, Command

from byakugan import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=byakugan', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name='byakugan-reporter',
    version=__version__,
    packages=find_packages(exclude=['docs', 'tests*']),
    url='',
    license='UNLICENSED',
    author='suusojeat',
    author_email='suusojeat@gmail.com',
    description='A program to scan all IP camera in a network.',
    long_description=long_description,
    keywords='cli',
    install_requires=['docopt'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': [
            'byakugan=byakugan.cli:main',
        ],
    },
    cmdclass={'test': RunTests},
)
