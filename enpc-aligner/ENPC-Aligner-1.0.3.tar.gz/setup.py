# -*- coding: utf-8 -*-
"""
    setup
    ~~~~
    Module d'alignements de textes traduits
    :license: MIT, see LICENSE for more details.
"""

from setuptools import setup
from os.path import join, dirname

with open(join(dirname(__file__), 'enpc_aligner/version.py'), 'r') as f:
    exec(f.read())

with open (join(dirname(__file__), 'requirements.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(
    name='ENPC-Aligner',
    version=__version__,
    description='Library of alignment of translated texts in differents languages',
    long_description="See documentation at https://github.com/PhilippeFerreiraDeSousa/bitext-matching/",
    keywords='alignment bitext ibm dtw',
    url='https://github.com/PhilippeFerreiraDeSousa/bitext-matching',
    author='Philippe Ferreira De Sousa',
    author_email='philippe@fdesousa.fr',
    license='MIT',
    packages=['enpc_aligner'],
    install_requires=install_requires,
    scripts=[
        'bin/align-example'
    ],
    zip_safe=False
)
