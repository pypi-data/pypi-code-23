#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 17:57:11 2018

@author: f2a
"""

from setuptools import setup



setup(
      name='cryptopass',
      version=__import__('cryptopass').__version__,
      author='f2a',
      author_email='empty@empty.com',
      packages=['cryptopass'],
      description='Safe and simple passwords manager',
      url='https://github.com/francof2a/cryptopass',
      license='MIT',
      keywords=['password', 'safe' ,'store'],
      install_requires=['pandas','pyperclip','cryptography'],
      entry_points={'console_scripts': ['cryptopass=cryptopass.console:main']},
      )


#py_modules=['./cryptopass/user_managment',
#                  './cryptopass/encrypt',
#                  './cryptopass/console'],
#scripts=['cryptopass'],
#        test_suite='tests',
#      classifiers=[
#              'Intended Audience :: End Users/Desktop',
#              'License :: OSI Approved :: MIT License',
#              'Operating System :: OS Independent',
#              'Programming Language :: Python :: 2',
#              'Programming Language :: Python :: 2.7',
#              'Programming Language :: Python :: 3',
#              'Programming Language :: Python :: 3.3',
#              'Programming Language :: Python :: 3.4',
#              'Programming Language :: Python :: 3.5',
#              'Programming Language :: Python :: 3.6',
#              'Programming Language :: Python',
#              'Environment :: Console',
#              'Topic :: Security'
#              ],