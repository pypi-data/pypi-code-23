# coding=utf-8
import os
import re

from setuptools import setup


def get_version(package):
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    return [dirpath for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='aiossdb',
    version=get_version('aiossdb'),
    author='Kevin',
    author_email='dgt_x@foxmail.com',
    description='aiossdb is a library for accessing a ssdb database from the asyncio',
    long_description=readme,
    license='MIT',
    keywords='aiossdb',
    packages=get_packages('aiossdb'),
    extras_require={
        'tests': [
            'pytest',
            'pytest-cov',
            'pytest-asyncio',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
