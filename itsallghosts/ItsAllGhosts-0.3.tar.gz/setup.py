#!/usr/bin/env python3

import os
from setuptools import setup

setup(
    name='ItsAllGhosts',
    version='0.3',
    long_description = open(os.path.join(os.path.dirname(__file__), "README.rst"),
                            "r", encoding="utf-8").read(),
    url="https://edugit.org/nik/itsallghosts",
    author="Dominik George",
    author_email="nik@naturalnet.de",
    packages=['itsallghosts'],
    zip_safe=False,
    install_requires=[
                      'aiohttp',
                      'psutil',
                      'xdg',
                     ],
    entry_points={
                  'console_scripts': [
                                  'itsallghosts = itsallghosts:main',
                                 ]
                 },
    classifiers=[
                 'Development Status :: 4 - Beta',
                 'Framework :: AsyncIO',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: POSIX',
                 'Programming Language :: Python :: 3 :: Only',
                 'Topic :: Text Editors',
                ],
)
