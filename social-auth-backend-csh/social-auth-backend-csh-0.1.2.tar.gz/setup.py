#!/usr/bin/env python

from setuptools import setup

setup(
    setup_requires=['pbr'],
    pbr=True,
)

import os
from setuptools import setup

requirements = [
    'social-auth-core',
]


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(
    name='social-auth-backend-csh',
    version='0.1.2',
    description='A Python Social Auth backend for Computer Science House',
    long_description=read('README.rst'),
    license='MIT',
    platforms='OS Independent',
    author='Steven Mirabito',
    author_email='smirabito@csh.rit.edu',
    url='http://pypi.python.org/pypi/social-auth-backend-csh',
    download_url='https://github.com/ComputerScienceHouse/social-auth-backend-csh/archive/0.1.2.tar.gz',
    keywords=('social', 'auth', 'oidc', 'openid', 'openid connect', 'csh', 'computer science house'),
    py_modules=['csh_auth'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=requirements,
)
