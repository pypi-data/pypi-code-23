# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

from setuptools import setup

setup(
    name='optconstruct',
    version='0.1.6',
    packages=['optconstruct'],
    entry_points={
        "console_scripts": ['optconstruct= optconstruct.optconstruct:main']
    },
    license='Apache 2.0',
    description='',
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest'
    ],
    install_requires=[
        'reformat',
    ],
    url='https://github.com/Frawless/optconstruct',
    author='Dominik Lenoch <dlenoch@redhat.com>, Jakub Stejskal <jstejska@redhat.com>, Zdenek Kraus <zkraus@redhat.com>',
    author_email='jstejska@redhat.com'
)