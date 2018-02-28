#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import re
from setuptools import setup, find_packages

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('brama/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='brama',
    version=version,
    python_requires='>={}.{}'.format(3, 5),
    url='https://github.com/kolyaflash/brama',
    license='MIT',
    author='Nikolay Baluk',
    author_email='kolyaflash@gmail.com',
    description='API Gateway proxy server with plugins',
    long_description=readme,
    packages=find_packages(exclude=['tests', 'docs', 'venv', 'examples']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'sanic>=0.7',
        'aiohttp>=3.0',
        'PyJWT',
    ],
    extras_require={
        'dev': [
            'pytest>=3',
            'pytest-localserver',
            'coverage',
            'tox',
            'sphinx',
            'flake8',
        ],
        'yaml': [
            'PyYAML>=3.12',
        ]
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    entry_points={
        'console_scripts': [
            'brama = brama.cli:main',
        ],
    },
)
