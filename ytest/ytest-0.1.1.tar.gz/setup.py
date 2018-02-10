#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
""" 打包的用的setup必须引入 """

VERSION = '0.1.1'

setup(name='ytest',
    version=VERSION,
    description="a demo project",
    long_description='just a simple demo',
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
        'console_scripts': [ 'ytest = app:main' ]
    },
)
