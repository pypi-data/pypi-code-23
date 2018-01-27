#!/usr/bin/env python
import codecs
import os
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as file_src:
        return file_src.read()


REQUIREMENTS = []

# Remember to sync with debinterface.__init__ and docs/conf.py
VERSION = "3.3.0"
URL = 'https://github.com/nMustaki/debinterface'


setup(
    name="debinterface",
    version=VERSION,
    description=("A simple Python library for dealing with "
                 "the /etc/network/interfaces file in most "
                 "Debian based distributions."),
    long_description=read("README.rst"),
    license="BSD",
    maintainer='Nathan Mustaki',
    maintainer_email='feydaykyn@gmail.com',
    author="Douglas Greenbaum",
    author_email="dggreenbaum@greenbad.org",
    url=URL,
    packages=find_packages(exclude=["test"]),
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': ['check-manifest', 'twine']
    },
    test_suite="test",
    download_url='{0}/archive/v{1}.zip'.format(URL, VERSION),
    keywords=['debian', 'network', 'system', 'configuration'],
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: System :: Systems Administration',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    )
)
