#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='ns_record',
    version='1.0.8',
    license="GPLv2",
    author='wangsir',
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
            'ns_mod_record = ns_record:main',
            'ns_get_wanip = ns_record:get_my_wan_ip'
        ]
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
