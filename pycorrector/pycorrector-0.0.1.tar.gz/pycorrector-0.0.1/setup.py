# -*- coding: utf-8 -*-
# Author: XuMing <xuming624@qq.com>
# Brief: 
# -*- coding: utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
import sys
LONGDOC = """
corrector
=====
# corrector
中文错别字纠正工具。音似、形似错字（或变体字）纠正，可用于中文拼音、笔画输入法的错误纠正。python开发。

**corrector** 依据语言模型检测错别字位置，通过拼音音似特征、笔画五笔编辑距离特征及语言模型困惑度特征纠正错别字。

### 语言模型
* Kenlm（统计语言模型工具）
* RNN（TensorFlow、PaddlePaddle均有实现栈式双向LSTM的语言模型）

安装说明
========

代码对 Python 2/3 均兼容

-  全自动安装： ``easy_install corrector`` 或者 ``pip install corrector`` / ``pip3 install corrector``
-  手动安装：将 corrector 目录放置于当前目录或者 site-packages 目录
-  通过 ``import corrector`` 来引用

"""

setup(name='pycorrector',
      version='0.0.1',
      description='Chinese Text Error corrector',
      long_description=LONGDOC,
      author='XuMing',
      author_email='xuming624@qq.com',
      url='https://github.com/shibing624/corrector',
      license="MIT",
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='NLP,correction,Chinese error corrector,corrector',
      packages=find_packages(),
	  install_requires=[
	  'kenlm==0.0.0',
	  'numpy>=1.13.1',
	  'pypinyin==0.30.0'
	  ],
      package_data={'corrector':['data/cn/*','*.py','LICENSE']})

