#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Setup script for entree
'''
import os

# from distutils.core import setup
from setuptools import setup, find_packages

_USERNAME = os.getenv('SUDO_USER') or os.getenv('USER')
_HOME = os.path.expanduser('~'+_USERNAME)
_CONFIGDIR = os.path.join(_HOME, '.config')


def get_template_dirs(path, basename='templates'):
    '''Get all path names for template directories
    '''
    dirs = []
    for fname in os.listdir(path):
        subpath = os.path.join(path, fname)
        if os.path.isdir(subpath):
            newbasename = os.path.join(basename, fname)
            dirs.append(newbasename)
            dirs.extend(get_template_dirs(subpath, basename=newbasename))
    return dirs

TEMPLATE_PATHS = [os.path.join(directory, '*')
                  for directory in ['templates'] +
                  get_template_dirs('entree/projects/templates')]
TEMPLATE_PATHS += [os.path.join(directory, '.gitignore')
                   for directory in ['templates'] +
                   get_template_dirs('entree/projects/templates')]

if os.path.exists(os.path.join(_CONFIGDIR, 'entree_config.json')):
    DATA_FILES = []
else:
    DATA_FILES = [(_CONFIGDIR, ['entree/entree_config.json'])]
DATA_FILES += [(_CONFIGDIR, ['entree_autocomplete'])]

setup(
    name='entree',
    version='2.3.2',
    description='',
    long_description='''
    Simple module to create files and directory structure necessary to
    start a programming project.

    Supported project types: HTML5, Python, Flask, Large Flask App, SQLAlchemy
    ''',
    author='Julien Spronck',
    author_email='github@frenetic.be',
    url='http://frenetic.be/',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['entree = entree:main']
    },
    data_files=DATA_FILES,
    package_data={
        'entree.projects': TEMPLATE_PATHS,
    },
    install_requires=[
        'certifi==2018.1.18',
        'chardet==3.0.4',
        'click==6.7',
        'Flask==0.12.2',
        'gunicorn==19.7.1',
        'idna==2.6',
        'itsdangerous==0.24',
        'Jinja2==2.10',
        'MarkupSafe==1.0',
        'requests==2.18.4',
        'six==1.11.0',
        'urllib3==1.22',
        'Werkzeug==0.14.1'
    ],
    license='Free for non-commercial use',
    download_url='https://github.com/frenetic-be/entree/archive/2.3.2.tar.gz'
)
