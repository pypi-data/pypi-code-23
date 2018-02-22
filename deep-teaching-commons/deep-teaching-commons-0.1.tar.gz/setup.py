#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='deep-teaching-commons',
    version='0.1',
    description='A Python module for common functionality across notebooks and teaching material.',
    author='Christoph Jansen',
    author_email='Christoph.Jansen@htw-berlin.de',
    url='https://gitlab.com/deep.TEACHING/deep-teaching-commons',
    packages=[
        'deep_teaching_commons',
        'deep_teaching_commons.data',
        'deep_teaching_commons.data.text'
    ],
    license='MIT',
    platforms=['any'],
    install_requires=[
        'requests'
    ]
)
