#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README') as f:
    readme = f.read()

setup(
    name='git-redmine',
    version='0.4.2',
    description='Git porcelain to interface with Redmine',
    long_description=readme,
    py_modules=['git_redmine'],
    author="Benjamin Dauvergne",
    author_email="bdauvergne@entrouvert.com",
    url="https://dev.entrouvert.org/projects/git-redmine/",
    install_requires=[
        'Click',
        'python-redmine',
        'GitPython',
    ],
    entry_points={
        'console_scripts': ['git-redmine=git_redmine:redmine'],
    }
)
