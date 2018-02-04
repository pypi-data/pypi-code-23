# -*- coding: utf-8 -*-
"""
    setup
    ~~~~
    Module d'alignements de textes traduits
    :license: MIT, see LICENSE for more details.
"""

from setuptools import setup
from os.path import join, dirname

def readme():
    with open('README.md') as f:
        return f.read()

with open(join(dirname(__file__), 'enpc_aligner/version.py'), 'r') as f:
    exec(f.read())

setup(
    name='ENPC-Aligner',
    version=__version__,
    description='Align bitexts',
    long_description=readme(),
    keywords='alignment bitext ibm dtw',
    url='https://github.com/PhilippeFerreiraDeSousa/bitext-matching',
    author='Philippe Ferreira De Sousa',
    author_email='philippe@fdesousa.fr',
    license='MIT',
    packages=['enpc_aligner'],
    scripts=[
        'bin/align-example'
    ],
    zip_safe=False
)
