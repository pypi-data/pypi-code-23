# encoding:utf-8

from setuptools import setup, find_packages  

setup(
    name='thrift4p',
    version='0.15b0',
    description="a python interface for thrift api in didapinche.",
    long_description=open("README.rst").read(),
    keywords='python thrift didapinche',  
    author='brown',
    author_email='317787106@qq.com', 
    url='http://gitlab.didapinche.com/dm/anticheating/tree/master/thrift4p', 
    packages=['thrift4p/gen-py','thrift4p'],

    include_package_data=True,
    zip_safe=False,  
    install_requires=[
        'kazoo',
        'thrift'
    ],
    entry_points={},
)
