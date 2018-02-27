#!/usr/bin/env python3
import os

from setuptools import setup

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, 'README.md')) as f:
    long_description = f.read()


setup(
    version='0.1.2',
    name='pipinator',
    description='Example Project to show how to package a Django project for pip',
    long_description=long_description,
    author='Anton Pirker',
    author_email='anton@ignaz.at',
    url='https://github.com/antonpirker/django-pip-project',
    keywords=['django'],
    license='MIT',
    entry_points={
        'console_scripts': [
            'pipinator = pipinator.__main__:main']
    },
    install_requires=[
        'Django==2.0.2',
        'easy-thumbnails==2.5',
        'ipdb',
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License',
    ]
)