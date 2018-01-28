import os
from setuptools import setup, find_packages

version='0.1.0'

setup(name='SimpleFTPServer',
      version=version,
      packages=find_packages(),
      description='Simple, Light FTP Server',
      author='Cook Green',
      url='https://github.com/cookgreen/SimpleFTPServer',
      license='GPL',
      install_requires=[
            'setuptools',
            'wxpython'
          ])
