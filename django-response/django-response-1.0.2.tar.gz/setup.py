# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.0.2'


setup(
    name='django-response',
    version=version,
    keywords='Django Response JSON',
    description='Django Response Relative',
    long_description=open('README.rst').read(),

    url='https://github.com/django-xxx/django-response',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['django_response'],
    py_modules=[],
    install_requires=['django-json-response'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)
