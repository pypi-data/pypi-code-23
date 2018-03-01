"""
Usage: pip install .[dev]
"""

import sys

from setuptools import setup

PKGNAME = 'hdf5_io'
PKGNAME_QUALIFIED = 'fsc.' + PKGNAME

with open('doc/description.txt', 'r') as f:
    DESCRIPTION = f.read()
try:
    with open('doc/README', 'r') as f:
        README = f.read()
except IOError:
    README = DESCRIPTION

with open('version.txt', 'r') as f:
    VERSION = f.read().strip()

if sys.version_info < (3, ):
    raise ValueError('only Python 3.x and higher are supported')

setup(
    name=PKGNAME_QUALIFIED,
    version=VERSION,
    packages=[PKGNAME_QUALIFIED],
    url='http://frescolinogroup.github.io/frescolino/pyhdf5io/' +
    '.'.join(VERSION.split('.')[:2]),
    include_package_data=True,
    author='C. Frescolino',
    author_email='frescolino@lists.phys.ethz.ch',
    description=DESCRIPTION,
    install_requires=['numpy', 'decorator', 'h5py', 'fsc.export'],
    extras_require={
        'dev':
        ['pytest', 'pytest-cov', 'yapf==0.20.2', 'prospector', 'pre-commit', 'sphinx', 'sphinx-rtd-theme', 'ipython>=6.2', 'matplotlib']
    },
    long_description=README,
    classifiers=[ # yapf: disable
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    license='Apache',
)
