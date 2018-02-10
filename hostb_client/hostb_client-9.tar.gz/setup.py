#!/usr/bin/env python3
# vi:si:et:sw=4:sts=4:ts=4
# encoding: utf-8
try:
    from setuptools import setup
except:
    from distutils.core import setup

def get_version():
    return 9 #import subprocess
    version = subprocess.check_output(['git', 'rev-list', 'HEAD', '--count']).decode()
    return version.strip()


setup(
    name="hostb_client",
    version=get_version(),
    description='''hostb_client is a command line client for hostb.''',
    author="j",
    author_email="j@mailb.org",
    url="https://r-w-x.org/r/hostb_client",
    license="GPLv3",
    scripts=[
        'bin/hostb_client',
    ],
    packages=[
        'hostb_client'
    ],
    install_requires=[
    ],
    keywords=[],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
)

