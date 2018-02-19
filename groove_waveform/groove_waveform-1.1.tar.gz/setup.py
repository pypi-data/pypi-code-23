#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages


setup(name='groove_waveform',
      version='1.1',
      description='waveform generation using libgroove',
      author='Basit Raza',
      author_email='basit.raza11@gmail.com',
      url='https://github.com/geek96/waveform-python',
      packages=find_packages(),
      package_data={
	    'waveform': ['waveform.cpython-36m-x86_64-linux-gnu.so'],
      }
  )
