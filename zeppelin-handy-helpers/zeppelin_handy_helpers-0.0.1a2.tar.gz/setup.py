import os
from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
from os import path
from codecs import open

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

requirements = [
    'enum',
    'requests',
    'animation'
]

test_requirements = [
    'mock'
]

setup(
    name='zeppelin_handy_helpers',
    version='0.0.1-alpha2',
    packages=['zeppelin_handy_helpers'],
    url='https://github.com/sbilello/zeppelin-handy-helper',
    download_url='https://github.com/sbilello/zeppelin-handy-helpers/archive/0.0.1-alpha2.tar.gz',
    license='MIT',
    author='Sergio Bilello',
    author_email='sergio.bilello@gmail.com',
    description='Console tool for zeppelin',
    long_description=long_description,
    scripts=[
        'scripts/zhh'
    ],
    install_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements,
    keywords=['helpers', 'console', 'zeppelin', 'notifier', 'monitoring'],
    classifiers=['Development Status :: 3 - Alpha','Programming Language :: Python :: 2.7']
)
