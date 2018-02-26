#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup

setup(
    name='qcloud_ccs',
    version='2.0.1',
    license="GPLv2",
    author='wanglin',
    author_email='wanglin@dbca.cn',
    url='https://newops.cn/15077893526985.html',
    description=u'以qcloud 容器服务sdk为基础. 1, 将机器创建/服务启停及更新等封装为接口;2.将机器和服务配置抽离为配置文件',
    packages=['qcloud_ccs'],
    install_requires=[
        'qcloudapi-sdk-python==2.0.7',
        'requests==2.18.4',
	    'pyyaml==3.12'
    ],
    entry_points={
        'console_scripts': [
            'qcloud_ccs=qcloud_ccs:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ]
)
