#!/usr/bin/env python
from setuptools import setup, find_packages
__author__ = 'adamkoziol'
setup(
    name="GenomeQAML",
    version="0.0.10",
    packages=['genomeqaml'],
    # package_data={'genomeqaml': ['*.msh', '*.p']},
    data_files=[('', ['genomeqaml/refseq.msh', 'genomeqaml/model.p', 'genomeqaml/dataframe.p'])],
    # include_package_data=True,
    license='MIT',
    scripts=['genomeqaml/classify.py'],
    author='OLC Bioinformatics',
    author_email='adam.koziol@inspection.gc.ca',
    description='CFIA OLC Genome Quality Assessment with Machine Learning',
    url='https://github.com/OLC-LOC-Bioinformatics/GenomeQAML',
    long_description=open('README.md').read(),
    install_requires=[
        'click',
        'biopython',
        'scipy',
        'pandas',
        'sklearn',
        'olctools'
    ]
)
