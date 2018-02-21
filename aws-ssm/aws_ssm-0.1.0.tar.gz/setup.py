#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='aws_ssm',
    version='0.1.0',
    packages=[ 'aws_ssm' ],
    install_requires=[ 'boto3' ],
    extras_require={
        "test": [ 'pytest>=3.0']
    },
    provides=[ 'aws_ssm' ],
    author='Justin Menga',
    author_email='justin.menga@gmail.com',
    url='https://github.com/mixja/aws-ssm',
    description='Decorator that injects AWS EC2 Systems Manager parameters as environment variables',
    keywords='aws ssm secrets',
    license='ISC',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: ISC License (ISCL)',
    ],
)