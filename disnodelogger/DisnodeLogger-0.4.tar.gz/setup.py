# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='DisnodeLogger',
    version="0.4",
    desription="Python port of disnode-logger on npm",
    long_description="Python port of disnode-logger on npm",
    author="Hazed SPaCEx",
    packages=find_packages(),
    py_modules=['DisnodeLogger'],
    include_package_data=False,
    install_requires=['colorama'],
    license='MIT',
    keywords='logger disnode'
)
