"""
Sf Tools for Python3 development

Author: SF-Zhou
Date: 2016-07-26

See:
https://github.com/sf-zhou/st
"""

from setuptools import setup, find_packages

setup(
    name='st',
    version='0.0.8',
    description='Sf Tools for Python3 Development',
    url='https://github.com/sf-zhou/st',

    author='SF-Zhou',
    author_email='sfzhou.scut@gmail.com',

    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='tools',
    packages=find_packages(exclude=['docs', 'tests']),
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    }
)
