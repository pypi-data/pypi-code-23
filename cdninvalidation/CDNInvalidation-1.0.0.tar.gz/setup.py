#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup

setup(
    name='CDNInvalidation',
    version='1.0.0',
    license="GPLv2",
    author='wanglin',
    author_email='wanglin@dbca.cn',
    url='https://newops.cn/15077893526985.html',
    description=u'使指定CloudFront对象缓存失效',
    packages=['CDNInvalidation'],
    install_requires=[
        'boto3'
    ],
    entry_points={
        'console_scripts': [
            'CDNInvalidation=CDNInvalidation:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
