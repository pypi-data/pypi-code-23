#!/usr/bin/env python
from setuptools import setup
__author__ = 'adamkoziol'
setup(
    name="GenomeQAML",
    version="0.0.1",
    include_package_data=True,
    license='MIT',
    scripts='genomeqaml/classify.py',
    author='OLC Bioinformatics',
    author_email='adam.koziol@inspection.gc.ca',
    description='CFIA OLC Genome Quality Assessment with Machine Learning',
    url='https://github.com/OLC-LOC-Bioinformatics/GenomeQAML',
    long_description=open('README.md').read(),
    py_modules=['extract_features'],
    install_requires=[
        'click',
        'biopython'
    ],
    entry_points='''
        [console_scripts]
        extract_features=extract_features:cli
    ''',
)
