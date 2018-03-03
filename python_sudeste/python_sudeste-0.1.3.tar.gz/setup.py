# -*- coding: utf-8 -*-
import pypandoc
from setuptools import setup

setup(
    name='python_sudeste',
    version='0.1.3',
    url='https://github.com/samukasmk/python-sudeste-module',
    license='Apache2',
    author='Samuel Sampaio',
    author_email='samukasmk@gmail.com',
    keywords='python_sudeste python sudeste',
    description='Módulo informativo do evento PythonSudeste',
    packages=['python_sudeste'],
    install_requires=[],
    long_description = pypandoc.convert('README.md', 'rst')
)
