#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals


from setuptools import setup

version_tuple = __import__('announcements').__version__
version = ".".join([str(v) for v in version_tuple])

setup(
    name='django-simple-announcements',
    description='Basic site-wide announcements for your Django project.',
    version=version,
    author='Craig de Stigter',
    author_email='craig.ds@gmail.com',
    url='https://github.com/craigds/django-simple-announcements/',
    packages=['announcements', 'announcements.templatetags'],
    package_data={'announcements': ['templates/announcements/*']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
