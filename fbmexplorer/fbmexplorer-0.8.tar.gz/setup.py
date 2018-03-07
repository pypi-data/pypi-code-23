#!/usr/bin/python3

from setuptools import setup
from io import open

setup(name='fbmexplorer',
      version='0.8',
      description='Parser to extract Facebook Messenger Data, and explorer it on d3.js tool.',
      long_description=open('README.rst').read(),
      url='https://github.com/adurivault/FBMessage',
      keywords=['facebook', 'chat', 'messenger', 'history', "visualization", "dataviz"],
      author="adurivault",
      author_email= "a.durivault@gmail.com",
      license='MIT',
      install_requires=[line.strip()
                      for line in open("requirements.txt", "r",
                                       encoding="utf-8").readlines()],
      scripts=['bin/fbm-parse'],
      packages=['fbmexplorer'],
      zip_safe=False)
