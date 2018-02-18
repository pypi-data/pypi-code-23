#!/usr/bin/python3.6

from setuptools import setup, find_packages

setup(
    name='tagfs',
    author='Pasha__kun',
    version='1.0.1b2',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tagfs = tagfs.__main__:main'
        ]
    }
)
