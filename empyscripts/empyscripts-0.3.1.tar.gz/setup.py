# -*- coding: utf-8 -*-
from setuptools import setup

readme = open('README.rst').read()

setup(
    name='empyscripts',
    version='0.3.1',
    description='Add-ons for empymod',
    long_description=readme,
    author='Dieter Werthmüller',
    author_email='dieter@werthmuller.org',
    url='https://empymod.github.io',
    download_url='https://github.com/empymod/empyscripts/tarball/v0.3.1',
    license='Apache License V2.0',
    packages=['empyscripts'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['numpy', 'scipy'],
)
