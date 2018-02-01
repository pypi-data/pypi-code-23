#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/23 9:45
# @Author  : chenjw
# @Site    : 
# @File    : setup.py
# @Software: PyCharm Community Edition
# @Desc    :  do what

import codecs
import os
import sys

try:
    from  setuptools import setup
except:
    from distutils.core import setup


def read(fname):
    """

    定义一个read方法，用来读取目录下的长描述

    我们一般是将README文件中的内容读取出来作为长描述，这个会在PyPI中你这个包的页面上展现出来，

    你也可以不用这个方法，自己手动写内容即可，

    PyPI上支持.rst格式的文件。暂不支持.md格式的文件，<BR>.rst文件PyPI会自动把它转为HTML形式显示在你包的信息页面上。

    """

    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


Name = 'ccommon'

PACKAGES = ["ccommon", ]

DESCRIPTION = "this is a package of common func"

LONG_DESCRIPTION = read("README.txt")

KEYWORDS = "cc package"

AUTHOR = "chenjw"

AUTHOR_EMAIL = "781354598@qq.com"

URL = "http://none"

VERSION = "1.0.11"

LICENSE = "MIT"

setup(

    name=Name,

    version=VERSION,

    description=DESCRIPTION,

    long_description=LONG_DESCRIPTION,

    classifiers=[

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',

        'Intended Audience :: Developers',

        'Operating System :: OS Independent',

    ],

    keywords=KEYWORDS,

    author=AUTHOR,

    author_email=AUTHOR_EMAIL,

    url=URL,

    license=LICENSE,

    packages=PACKAGES,

    include_package_data=True,

    zip_safe=True,

)
