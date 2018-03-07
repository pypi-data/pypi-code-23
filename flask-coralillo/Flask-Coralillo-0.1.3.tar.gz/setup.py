#!/usr/bin/env python3
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='Flask-Coralillo',
    version='0.1.3',
    url='https://github.com/getfleety/flask-coralillo',
    license='MIT',
    author='Abraham Toriz Cruz',
    author_email='categulario@gmail.com',
    description='Flask module for the Coralillo redis ORM',
    long_description=long_description,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'coralillo',
    ],
    test_suite = 'flask_coralillo.tests.test_flask_coralillo',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
