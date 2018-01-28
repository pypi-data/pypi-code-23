import os
from setuptools import setup

version='0.1.0'

setup(name='Mount&BladeServerMonitor',
      version=version,
      description='Server Monitor Tool for Mount&Blade series games',
      author='Cook Green',
      url='https://github.com/cookgreen/MBServerMonitor',
      license='GPL',
      install_requires=[
            'setuptools',
            'wxpython'
          ])
