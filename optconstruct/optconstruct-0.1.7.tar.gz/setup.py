# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

from setuptools import setup, find_packages

setup(
    name='optconstruct',
    version='0.1.7',
    packages=find_packages(exclude=['build', 'docs', 'templates', 'optconstruct.types.composed']),
    entry_points={
        "console_scripts": ['optconstruct= optconstruct.optconstruct:main']
    },
    license='Apache 2.0',
    description='This package provides an API for create appropriate option for command to execute in your application. API is called by one of several classes, which each of them handle different type of option.',
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