#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'elasticsearch-dsl>=2.0,<3.0',
    'pytimeparse>=1.1,<2.0'
]

test_requirements = [
    'flake8==2.6.0',
    'tox==2.3.1',
    'coverage==4.1',
    'Sphinx==1.7.0',
    'cryptography==1.7',
    'PyYAML>=3.11,<4.0',
    'pytest>=2.9.2,<3.0',
    'certifi',
]

setup(
    name='log_hunter',
    version='0.5.2',
    description="Library and CLI tool to access kibana logglines in bulk.",
    long_description=readme + '\n\n' + history,
    author="Peter Tillemans",
    author_email='pti@melexis.com',
    url='https://github.com/ptillemans/log_hunter',
    packages=find_packages('src'),
    package_dir={'':'src'},
    entry_points={
        'console_scripts': [
            'log_hunter=log_hunter.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='log_hunter',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=['bump2version']
)
