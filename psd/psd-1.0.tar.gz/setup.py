#!/usr/bin/env python3
"""Setup file for pip module."""

from setuptools import setup

setup(
    name='psd',
    version='1.0',
    description='Python tools for data visualization and spectral analysis.',
    url='https://gitlab.in2p3.fr/j2b.bayle/psd',
    author='Jean-Baptiste Bayle (APC/CNRS/CNES)',
    author_email='bayle@apc.in2p3.fr',
    license='GNU GPLv3',
    packages=['psd'],
    install_requires=[
        'argparse',
        'numpy',
        'scipy',
        'matplotlib',
    ],
    entry_points = {
        'console_scripts': ['psd=psd.psd:main'],
    },
    zip_safe=False,
)
