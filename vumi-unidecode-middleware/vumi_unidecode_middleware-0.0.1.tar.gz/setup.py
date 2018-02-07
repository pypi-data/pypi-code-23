#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='vumi_unidecode_middleware',
    version='0.0.1',
    url='https://github.com/praekeltfoundation/vumi-unidecode-middleware',
    license='BSD',
    description='Vumi middleware that runs message content through unidecode',
    long_description=open('README.md').read(),
    author='Praekelt.org',
    author_email='dev@praekelt.org',
    packages=find_packages(),
    install_requires=[
        'unidecode',
        'vumi',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
