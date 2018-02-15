#!/usr/bin/env python

import os

try:
    from setuptools import setup
except ImportError:
    print("setuptools module not found.")
    from sys import exit
    exit(1)

os.system("gzip doc/*")

setup(
    name='pkg-anonymize',
    version='0.0.2',
    license='BSD',
    url='https://github.com/lognoz/anonymize',
    description='A program that help to protect your privacy against global mass surveillance and been secure on the web.',
    author='Marc-Antoine Loignon',
    author_email='info@lognoz.com',
    platforms=['Linux'],
    packages=['anonymize', 'anonymize.core'],
    data_files=[
        ('/usr/share/bash-completion/completions', ['completion/anonymize']),
        ('/usr/lib/systemd/system', ['service/anonymize.service']),
        ('/usr/share/man/man1', ["doc/anonymize.1.gz"])
    ],
    entry_points={
        'console_scripts': [
            'anonymize = anonymize.main:main'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)

os.system("gunzip doc/*.gz")
