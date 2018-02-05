#!/usr/bin/env python


""" Setup script """


import os

import setuptools


NAME = 'rst2sh5'
DESCRIPTION = "Docutils writer outputting semantic HTML5"


AUTHOR = 'sinoroc'
AUTHOR_EMAIL = 'sinoroc.code+python@gmail.com'
URL = 'https://github.com/sinoroc/rst2sh5'


LICENSE = 'Apache-2.0'  # https://spdx.org/licenses/


REQUIREMENTS_INSTALL = [
    'beautifulsoup4',
    'docutils',
    'html5lib',
    'setuptools',  # needed for 'pkg_resources'
]


REQUIREMENTS_PACKAGE = [
    'pex',
    'twine',
    'wheel',
]


REQUIREMENTS_TEST = [
    'pytest',
    'pytest-pep8',
    'pytest-pylint',
    'readme_renderer',  # for 'setup.py check --restructuredtext'
]


REQUIREMENTS_EXTRAS = {
    'package': REQUIREMENTS_PACKAGE,
    'test': REQUIREMENTS_TEST,
}


ENTRY_POINTS = {
    'console_scripts': [
        '{}={}.main:entry_point'.format(NAME, NAME),
    ],
}


def _do_setup():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.rst')) as file_:
        readme = file_.read()
    with open(os.path.join(here, 'CHANGELOG.rst')) as file_:
        changelog = file_.read()

    long_description = readme
    version = changelog.splitlines()[4]

    source_directory = 'src'
    packages = setuptools.find_packages(
        where=source_directory,
    )
    package_directories = {
        '': source_directory,
    }

    setuptools.setup(
        name=NAME,
        version=version,
        # metadata
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        license=LICENSE,
        long_description=long_description,
        url=URL,
        # options
        entry_points=ENTRY_POINTS,
        extras_require=REQUIREMENTS_EXTRAS,
        install_requires=REQUIREMENTS_INSTALL,
        package_dir=package_directories,
        packages=packages,
    )
    return


if __name__ == '__main__':
    _do_setup()


# EOF
