#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='git-redmine',
    version='0.4',
    description='Git porcelain to interface with Redmine',
    py_modules=['git_redmine'],
    install_requires=[
        'Click',
        'python-redmine',
        'GitPython',
    ],
    entry_points={
        'console_scripts': ['git-redmine=git_redmine:redmine'],
    }
)
