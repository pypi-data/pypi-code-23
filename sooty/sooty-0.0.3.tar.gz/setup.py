# -*- coding: utf-8 -*-

from setuptools import setup

version = '0.0.3'

requires = ['docopt', 'psycopg2']

with open('README.rst') as f:
    readme = f.read()

setup(
    name='sooty',
    version=version,
    description='Sooty: Simple database migrator.',
    long_description=readme,
    author='Jeff Zellman',
    author_email='jzellman@gmail.com',
    url='https://github.com/jzellman/sooty',
    license='ISC',
    py_modules=['sooty'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    entry_points = {
        'console_scripts': ['sooty=sooty:cli'],
    },
    install_requires=requires,
    zip_safe=False
)
