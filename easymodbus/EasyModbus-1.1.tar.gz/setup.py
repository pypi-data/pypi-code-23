#!/usr/bin/env python3
from distutils.core import setup


setup(
    name='EasyModbus',
    packages = ['EasyModbus'],
    version      = '1.1',
    license      = 'GPLv3',
    author       = 'Stefan Rossmann',
    author_email = 'info@rossmann-engineering.de',
    url          = 'https://github.com/rossmann-engineering/EasyModbusTCP.PY',
    description='THE standard library for Modbus RTU and Modbus TCP',
    install_requires=[
          'serial',
      ],
    keywords='easymodbus modbus serial RTU TCP EasyModbusTCP',
    classifiers=[
       'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Communications :: Email',
          'Topic :: Office/Business',
          'Topic :: Software Development :: Bug Tracking',
    ]
)