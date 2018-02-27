#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension


setup(
    name='cryio',
    version='2018.2.27',
    description='Crystallographic IO routines',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/cryio',
    license='GPLv3',
    install_requires=[
        'numpy',
        'jinja2',
    ],
    packages=[
        'cryio',
        'cryio.templates',
    ],
    ext_modules=[
        Extension(
            'cryio._cryio', [
                'src/cryiomodule.c',
                'src/agi_bitfield.c',
                'src/byteoffset.c',
                'src/mar345.c',
            ],
        )
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
