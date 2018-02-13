#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import
from __future__ import print_function

import io
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read().strip()


setup(
    name='photowrench',
    version=read('VERSION'),
    description='Tool to perform photography related tasks',
    long_description=read('README.rst'),
    author='Bor González Usach',
    author_email='bgusach@gmail.com',
    url='https://github.com/bgusach/photowrench',
    license='MPL-2.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords=[],
    install_requires=[
        'click',
        'exifread',
    ],
    entry_points={
        'console_scripts': [
            'photowrench=photowrench.__main__:main',
        ]
    },
)

