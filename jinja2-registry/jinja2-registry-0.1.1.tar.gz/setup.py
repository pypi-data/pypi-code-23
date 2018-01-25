#!/usr/bin/env python
'''
    jinja2-registry: Template namespacing convenience library for Jinja2
'''

from distutils.core import setup
from setuptools import find_packages

CLASSIFIERS = [
'Development Status :: 4 - Beta',
'Programming Language :: Python',
'Programming Language :: Python :: 2.7',
'Programming Language :: Python :: 3.3',
'Programming Language :: Python :: 3.4',
'Programming Language :: Python :: 3.5',
'Operating System :: Microsoft :: Windows',
'Operating System :: POSIX',
'Operating System :: Unix',
'Operating System :: MacOS',
'Natural Language :: English',
]

with open('README.rst') as f:
    LONG_DESCRIPTION = ''.join(f.readlines())

setup(
    name = 'jinja2-registry',
    version = '0.1.1',
    packages = find_packages(),
    install_requires = ['Jinja2>=2.6',
                       ],
    author = '3point Science',
    author_email = 'info@3ptscience.com',
    description = 'jinja2-registry',
    long_description = LONG_DESCRIPTION,
    keywords = 'templating',
    url = 'https://3ptscience.com',
    download_url = 'http://github.com/3ptscience/jinja2-registry',
    classifiers=CLASSIFIERS,
    platforms = ['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    license='MIT License',
    use_2to3 = False,
)
