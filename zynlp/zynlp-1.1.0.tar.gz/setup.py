#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='zynlp',
    version='1.1.0',
    description=(
        'some nlp tools writes by zy'
    ),
    long_description=open('README.rst').read(),
    author='zhongyuan',
    author_email='zhongyuan.nlp@gmail.com',
    maintainer='zhongyuan',
    maintainer_email='zhongyuan.nlp@gmail.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='http://www.zynlp.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[]
)