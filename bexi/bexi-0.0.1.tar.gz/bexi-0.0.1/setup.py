#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

__VERSION__ = '0.0.1'

assert sys.version_info[0] == 3, "We require Python > 3"

setup(
    name='bexi',
    version=__VERSION__,
    description=(
        'BitShares Exchange Integration (BEXI).'
        'A toolkit that allows to deal with deposits and withdrawals on'
        'the BitShares Blockchain.'
    ),
    long_description="",
    download_url='',
    author='Blockchain Projects BV',
    author_email='info@BlockchainProjectsBV.com',
    maintainer='Blockchain Projects BV',
    maintainer_email='info@BlockchainProjectsBV.com',
    url='http://blockchainprojectsbv.com',
    keywords=['bitshares'],
    packages=find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    entry_points={
    },
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
