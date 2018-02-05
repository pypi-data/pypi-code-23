import os

from setuptools import setup, find_packages



setup(
	name='dexseq_prepare_annotation2',
	version='1.0.0',
	description='Subread_to_DEXSeq python package',
	long_description='PROGRAM TO PREPARE ANNOTATION FILES FOR FEATURECOUNTS AND DEXSEQ AND TRANSFORM FEATURECOUNTS EXPRESSIONS OUTPUT INTO DEXSEQ INPUT',
	url='https://github.com/jvrakor/Subread_to_DEXSeq',
	download_url = 'https://github.com/jvrakor/Subread_to_DEXSeq/tarball/v1.0.0',
	

	classifiers=[],

	keywords=['bioinformatics','dexseq', 'featurecounts', 'annotation'],

	packages=find_packages(),

	install_requires=['HTSeq>=0.9.0'],
	extras_require={},

	entry_points={
	    'console_scripts': [
	        'dexseq_prepare_annotation2=dexseq_prepare_annotation2:main',
	        ]
	    },

)

