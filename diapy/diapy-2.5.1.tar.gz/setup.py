#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='diapy',
    version='2.5.1',
    description='A rough diary manager based on python.',
    long_description='''A rough diary manager based on python.
Diapy uses cryptography.fernet to encrypt your top secret.''',
    url='https://github.com/FiftysixTimes7/diapy',
    author='FiftysixTimes7(PTJ)',
    author_email='pangtj26@163.com',
    license='MIT',
    classifiers=['License :: OSI Approved :: MIT License',
                 'Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3 :: Only',
                 'Topic :: Utilities'],
    keywords='diary',
    packages=find_packages(),
    python_requires='>=3',
    install_requires=['cryptography'],
)
