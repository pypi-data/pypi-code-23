#!/usr/bin/env python3
#
# skuld - tiny script for generating an AWS profile with the AWS 2FA.
# Copyright (c) 2017 Stanislas Nanchen <stan@deep-impact.ch>

import os
from setuptools import setup

try:
    readme = open(os.path.join(os.path.dirname(__file__), "README.md")).read()
except:
    readme = "See: http://pypi.python.org/pypi?name=skuld&:action=display_pkginfo"

setup(
        name='skuld',
        description='Generate an AWS profile with the 2FA authentication from CLI',
        long_description=readme,
        version='1.1.5',
        author='Stanislas Nanchen',
        author_email='stan@deep-impact.ch',
        license="Apache2",
        keywords="AWS 2FA CLI",
        platforms=['MacOS X; Linux'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            ],
        install_requires=[
            'awscli>=1.10.0',
            'requests>=2.18.4'
            ],
        packages=['skuld'],

        entry_points={
            'console_scripts': [
                'skuld = skuld.skuld:main',
                'ec2skuld = skuld.ec2skuld:main',
                ]
            },
        )
