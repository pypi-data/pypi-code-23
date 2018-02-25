#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='xlsx2json',
    version='0.0.3',
    description='Convert XLSX to JSON and include hyperlinks.',
    author='Data Dais',
    author_email='code@datadais.com',
    url='https://code.datadais.com/',
    packages=find_packages(exclude=['tests', '.cache', '.venv', '.git', 'dist']),
    include_package_data=True,
    install_requires=[
        'Click',
        'backports.tempfile',
        'openpyxl',
    ],
    entry_points='''
        [console_scripts]
        xlsx2json=xlsx2json.cli:entry_point
    ''',
)
