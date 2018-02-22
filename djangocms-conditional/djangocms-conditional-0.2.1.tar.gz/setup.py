#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import djangocms_conditional

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = djangocms_conditional.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()
if sys.argv[-1] == 'test':
    os.system('djangocms-helper djangocms_conditional test --cms --nose')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='djangocms-conditional',
    version=version,
    description="""django CMS plugin that shows content based on user group membership.""",
    long_description=readme + '\n\n' + history,
    license='GPLv2+',
    author='Roy Hooper',
    author_email='rhooper@toybox.ca',
    url='https://github.com/rhooper/djangocms-conditional',
    packages=[
        'djangocms_conditional',
    ],
    include_package_data=True,
    install_requires=[
        'django-cms>=3.4',
    ],
    zip_safe=False,
    keywords='djangocms-conditional',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)