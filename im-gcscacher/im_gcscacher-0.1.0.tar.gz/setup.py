#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dist = setup(
    name='im_gcscacher',
    version='0.1.0',
    description='A decorator for caching into gcs on google app engine, python standard environment',
    author='Emlyn O\'Regan',
    author_email='emlynoregan@gmail.com',
    url='https://github.com/emlynoregan/im_task',
    license='../LICENSE.txt',
    packages=['im_gcscacher'],
    install_requires=['im_util', 'GoogleAppEngineCloudStorageClient', 'cloudpickle'],
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
