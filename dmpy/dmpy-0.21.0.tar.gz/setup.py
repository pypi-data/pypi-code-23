#!/usr/bin/env python
import json
import os

from setuptools import setup, find_packages


def get_requirements_from_pipfile_lock(pipfile_lock=None):
    if pipfile_lock is None:
        pipfile_lock = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Pipfile.lock')
    lock_data = json.load(open(pipfile_lock))
    return [package_name for package_name in lock_data.get('default', {}).keys()]


pipfile_lock_requirements = get_requirements_from_pipfile_lock()
setup(
    name='dmpy',
    version='0.21.0',
    description='Distributed Make for Python',
    long_description=open('README.rst').read(),
    author='Kiran Garimella, Warren Kretzschmar',
    author_email='kiran.garimella@gmail.com, winni@warrenwk.com',
    packages=find_packages(),
    install_requires=pipfile_lock_requirements,
    url='https://github.com/kvg/dmpy',
    include_package_data=True,
)
