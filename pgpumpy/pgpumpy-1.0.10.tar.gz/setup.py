# setup.py

from setuptools import setup

with open("README", 'r') as f:
    long_description = f.read()

setup(
   name='pgpumpy',
   version='1.0.10',
   description='A data pump for PostgreSQL, implemented as a Python module.',
   license="Mozilla Public License 2.0 (MPL 2.0)",
   long_description='A data pump for PostgreSQL, implemented as a Python module.',
   author='Phenicle',
   author_email='pheniclebeefheart@gmail.com',
   url="https://github.com/phenicle/pgpumpy",
   packages=['pgpumpy',],  #same as name
   install_requires=['cfgpy'], #external packages as dependencies
)
