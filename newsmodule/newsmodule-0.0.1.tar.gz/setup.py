# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from setuptools import setup, find_packages

setup(
    name='newsmodule',
    version='0.0.1',
    keywords=('newsmodule'),
    description='newsmodule log collection',
    license='MIT License',
    install_requires=['Django>=1.8', 'djangorestframework>=3.1.3'],
    author='cq',
    author_email='chenq310@126.com',
    packages=find_packages(),
    platforms='any',


)