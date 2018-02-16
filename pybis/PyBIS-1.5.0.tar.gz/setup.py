import os
import sys

if sys.version_info < (3,3):
    sys.exit('Sorry, Python < 3.3 is not supported')

from setuptools import setup


setup(
    name='PyBIS',
    version= '1.5.0',
    description='openBIS connection and interaction, optimized for using with Jupyter',
    url='https://sissource.ethz.ch/sispub/pybis/',
    author='Swen Vermeul |  ID SIS | ETH Zürich',
    author_email='swen@ethz.ch',
    license='BSD',
    packages=[
        'pybis',
    ],
    install_requires=[
        'pytest',
        'requests',
        'datetime',
        'pandas',
        'click',
        'texttable',
        'tabulate',
    ],
    python_requires=">=3.3"
)
