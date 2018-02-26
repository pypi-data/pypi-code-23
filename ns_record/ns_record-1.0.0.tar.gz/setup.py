#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='ns_record',
    version='1.0.0',
    license="GPLv2",
    author='wanglin',
    author_email='wanglin@dbca.cn',
    url='https://newops.cn/15077893526985.html',
    description=u'修改云厂商域名解析记录',
    packages=['ns_record'],
    install_requires=[
        'qcloudapi-sdk-python>=2.0.11',
        'requests>=2.4.3'
    ],
    entry_points={
        'console_scripts': [
            'ns_record_mod=ns_record:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
