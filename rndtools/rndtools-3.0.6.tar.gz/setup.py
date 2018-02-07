#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'numpy >= 1.10',
    'scipy >= 0.11.0',
    'matplotlib >= 1.4',
    'keras >= 2.0',
    'click >= 5.0',
    'contexttimer >= 0.3.3',
    'hickle >= 2.1.0',
    'scikit-learn >= 0.18',
    'six >= 1.11',
    'pathos >= 0.2',
    'tqdm >= 4.19',
]

tests_require = [
    'Tensorflow >= 1.0',
    'mock',
    'nose',
]


def readme():
    return open('index.rst').read()


setup(
    name='rndtools',
    version='3.0.6',
    description='R&D tools',
    long_description=readme(),
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="nose.collector",
    url="https://gitlab.com/identt-rnd/rnd-tools",
    maintainer='Damian Mirecki',
    maintainer_email='damian.mirecki@identt.pl',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
