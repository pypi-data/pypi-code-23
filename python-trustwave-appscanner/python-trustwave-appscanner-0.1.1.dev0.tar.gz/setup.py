#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

try:
    long_description = open('README.md').read()
except:
    long_description = ''

setup(
    name='python-trustwave-appscanner',
    version="0.1.1.dev",
    description='A wrapper around the tapioca-trustwave-appscanner for'
                ' translating the Appscanner API documents into Python Objects',
    long_description=long_description,
    author="Flávio Cardoso Ferreira Pontes",
    author_email="flavio.pontes@siteblindado.com.br",
    url='https://github.com/siteblindado/python_trustwave_appscanner',
    packages=[
        'appscanner',
    ],
    package_dir={'appscanner': 'appscanner'},
    package_data={
        '': ['LICENSE.txt', 'README.md', '*.xml', '*.xsd']
    },
    include_package_data=True,
    install_requires=[
        'tapioca-trustwave-appscanner',
        'lxml==4.1.1'
    ],
    license="MIT",
    zip_safe=False,
    keywords='trustwave',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests'
)