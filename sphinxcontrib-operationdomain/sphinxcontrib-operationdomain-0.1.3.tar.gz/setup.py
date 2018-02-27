# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the sphinxcontrib-operationdomain Sphinx extension.

It needs Sphinx 1.0 or newer.
'''

setup(
    name='sphinxcontrib-operationdomain',
    version='0.1.3',
    url='https://bitbucket.org/togakushi/sphinxcontrib-operationdomain',
    license='BSD',
    author='togakushi',
    author_email='nina.togakushi@gmail.com',
    description='Sphinx extension sphinxcontrib-operationdomain',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=['sphinxcontrib.operationdomain'],
    include_package_data=True,
    install_requires=[
        'Sphinx>=1.0'
    ],
)
