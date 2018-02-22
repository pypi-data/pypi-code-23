#!/usr/bin/env python

from setuptools import setup

setup(
    name='django-webprofiler',
    version='0.1.2',
    description='',
    author='Alex Oleshkevich',
    author_email='alex.oleshkevich@gmail.com',
    url='https://github.com/alex-oleshkevich/django-webprofiler',
    license='MIT',
    install_requires=[
        'Django>=1.11',
        'python-box',
        'pygments',
        'sqlparse',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
