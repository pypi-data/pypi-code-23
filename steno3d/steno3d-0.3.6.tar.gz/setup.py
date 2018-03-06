#!/usr/bin/env python
'''
    steno3d: Client library for Steno3D & steno3d.com
'''

from distutils.core import setup
from setuptools import find_packages

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Physics',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Operating System :: MacOS',
    'Natural Language :: English',
]

with open('README.rst') as f:
    LONG_DESCRIPTION = ''.join(f.readlines())

setup(
    name='steno3d',
    version='0.3.6',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.7',
        'pypng',
        'requests',
        'six',
        'properties==0.4.0',
        'vectormath',
    ],
    author='Seequent',
    author_email='support@steno3d.com',
    description='Steno3D Python client library',
    long_description=LONG_DESCRIPTION,
    keywords='visualization',
    url='https://steno3d.com/',
    download_url='http://github.com/aranzgeo/steno3dpy',
    classifiers=CLASSIFIERS,
    platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    license='MIT License',
    use_2to3=False,
)
