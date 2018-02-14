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
    version='0.0.1',
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
    }
)

os.system("gunzip doc/*.gz")
