import os

from setuptools import setup

setup(
    name='algmarket',
    version='1.0.0',
    description='Algmarket Python Client',
    long_description='Algmarket Python Client is a client library for accessing Algorithmia from python code. This library also gets bundled with any Python algorithms in Algmarket.',
    url='https://github.com/qihe1126/algmarket-python',
    license='MIT',
    author='erniu',
    author_email='qihea163@163.com',
    packages=['Algmarket'],
    install_requires=[
        'requests',
        'six',
        'enum34'
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
