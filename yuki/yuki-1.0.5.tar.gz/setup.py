import sys
import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['tests']

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'YUKI_VERSION')) as version_file:
    version = version_file.read().strip()

with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name = 'yuki',
    version = version,
    description = 'CEPC software management toolkit',
    long_description = long_description,
    url = 'https://github.com/cepc/cepcenv',
    author = 'Mingrui Zhao',
    author_email = 'mingrui.zhao@mail.labz0.org',
    license = 'MIT',

    classifiers = [
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: System :: Software Distribution',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],

    keywords = 'Data',
    packages = find_packages(exclude=[]),
    install_requires = [
        'click',
    ],
    include_package_data = True,
    tests_require = [
        'pytest',
    ],
    entry_points = {
        'console_scripts': [
            'yuki = Yuki:main',
        ],
    },
    # cmdclass = {'test': PyTest},
)
