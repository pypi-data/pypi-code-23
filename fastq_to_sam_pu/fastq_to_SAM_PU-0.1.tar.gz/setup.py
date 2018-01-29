#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'fastq_to_SAM_PU',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.1,
      description = 'extract a PU value from a fastq record',
      url = 'https://github.com/NCI-GDC/fastq-to-SAM-PU',
      license = 'Apache 2.0',
      packages = find_packages(),
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      entry_points={
          'console_scripts': ['fastq_to_SAM_PU=fastq_to_SAM_PU.__main__:main']
      },
)
