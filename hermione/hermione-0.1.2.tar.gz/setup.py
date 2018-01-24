#!/usr/bin/env python

from setuptools import setup

version = '0.1.2'

required = open('requirements.txt').read().split('\n')

setup(
    name='hermione',
    version=version,
    description='Joyplots in Python with seaborn-style interface',
    author='Olga Botvinnik',
    author_email='olga.botvinnik@gmail.com',
    url='https://github.com/czbiohub/hermione',
    packages=['hermione'],
    install_requires=required,
    long_description='See ' + 'https://github.com/czbiohub/hermione',
    license='MIT'
)
