#!/usr/bin/env python

"""
distutils/setuptools install script.
"""

import quantgo_api

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup


packages = ['quantgo_api', ]

requires = ['argparse>=1.1',
            'future',
			'boto3>=1.4.0',
			'numpy>=1.11.0',
			'pandas>=0.18.0',
            ]


setup(
    name='quantgo-api',
    version=quantgo_api.__version__,
    description='QuantGo Python API and Command Line Tool.',
    long_description=open('README.md').read(),
    author='Yuri Poliukhovich',
    author_email='yuri@quantgo.com',
    url='https://quantgo.com',
    scripts=['bin/qg_cli', 'bin/qg_cli.bat'],
    packages=packages,
    package_dir={'quantgo_api': 'quantgo_api'},
    install_requires=requires,
    license=open("LICENSE.txt").read(),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Intended Audience :: End Users/Desktop',
    ),
    keywords=['quantgo', 'quantgo-api']
)
