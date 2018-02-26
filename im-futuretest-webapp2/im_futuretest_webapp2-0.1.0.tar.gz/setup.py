#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dist = setup(
    name='im_futuretest_webapp2',
    version='0.1.0',
    description='webapp2 handlers and route utils for im_futuretask, for Google App Engine, Python standard environment',
    author='Emlyn O\'Regan',
    author_email='emlynoregan@gmail.com',
    url='https://github.com/emlynoregan/im_futuretest_webapp2',
    license='../LICENSE.txt',
    packages=['im_futuretest_webapp2'],
    install_requires=['im_futuretest >= 0.1.4'],
    long_description=open('../README.md').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
    ]
)
