#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
from os import path
""" 打包的用的setup必须引入 """
here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

VERSION = '0.1.4'

setup(name='ytest',
    version=VERSION,
    description="a demo project",
    long_description=long_description, # Optional
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='python ytest demo',
    author='yotong',
    author_email='yotong@qq.com',
    url='https://github.com/yotong/ytest',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[ 'requests', ],
    entry_points={
        'console_scripts': [ 'ytool = ytest:main' ]
    },
)
