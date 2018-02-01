"""Setuptools based setup module for Simulagora client."""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='simulagora',
    version='0.3.0',
    description='A python library to use Simulagora programatically',
    long_description=long_description,
    url='http://www.cubicweb.org/project/simulagora-client',
    author='LOGILAB S.A. (Paris, FRANCE)',
    author_email='contact@logilab.fr',
    classifiers = [
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
    ],
    keywords='simulagora cubicweb cwclientlib',
    packages=find_packages(exclude=['contrib', 'debian', 'test']),
    install_requires=[
        'cwclientlib >= 0.3.0',
    ],
    entry_points={
        'console_scripts': [
            'simulagora=simulagora.__main__:main',
        ],
    },
)
