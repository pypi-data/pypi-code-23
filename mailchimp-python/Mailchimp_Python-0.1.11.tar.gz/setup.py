# coding=utf-8
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Mailchimp Python',
    version='0.1.11',
    description='A package used to integrate with Mailchimp via their public API (version 3)',
    long_description=long_description,
    url="https://github.com/andreask/mailchimp-python",
    author='Andréas Kühne',
    author_email='andreas@kuhne.se',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='mailchimp integration api',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests', 'python-dateutil'],
    test_suite="tests",
    tests_require=['responses']
)
