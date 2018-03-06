#!/usr/bin/env python

from setuptools import setup

setup(
  name='mummichog1',
  version='1.0.11',

  author='Shuzhao Li, Andrei Todor',
  author_email='shuzhao.li@gmail.com',
  description='Pathway and network analysis for metabolomics data',
  url='http://mummichog.org',
  license='MIT',
  packages=['mummichog1', 'mummichog1/pydata'],

  include_package_data=True,
  zip_safe=False,
  entry_points = {
        'console_scripts': ['mummichog1=mummichog1.command_line:main'],
    },

  install_requires=[
    'xlsxwriter',
    'networkx>=1,<2',
    'numpy',
    'scipy',
  ],

)
