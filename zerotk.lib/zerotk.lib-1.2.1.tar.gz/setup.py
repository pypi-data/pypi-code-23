#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='zerotk.lib',
    use_scm_version=True,

    author="Alexandre Andrade",
    author_email='kaniabi@gmail.com',

    url='https://github.com/zerotk/zerotk.lib',

    description="Collection of basic Pytho utilities.",
    long_description="Collection of basic Pytho utilities.",

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='',

    include_package_data=True,
    packages=['zerotk', 'zerotk.lib'],
    namespace_packages=['zerotk'],
    install_requires=[
        'ruamel.yaml',
        'semantic_version',
        'pathspec',
    ],
    dependency_links=[
    ],
    setup_requires=['setuptools_scm'],
    tests_require=[
        'pytest',
        'datadiff',
    ],

    license="MIT license",
)
