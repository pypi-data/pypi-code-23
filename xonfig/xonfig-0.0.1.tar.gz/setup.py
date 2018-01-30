# -*- coding: utf-8 -*-

from setuptools import setup

from version import version

setup(name='xonfig',
      description='Python configparser wrapper',
      keywords=['config', 'parser', 'configparser'],
      version=version,
      author='Talha Buğra Bulut',
      author_email='talhabugrabulut@gmail.com',
      url='https://github.com/talhasch/xonfig',
      py_modules=['xonfig', 'version']
      )
