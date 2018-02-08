# setup.py

from setuptools import setup

with open("README", 'r') as f:
    long_description = f.read()

setup(
   name='cfgpy',
   version='1.0.6',
   description='A simple, flexible, and powerful config reader for Python',
   license="Mozilla Public License 2.0 (MPL 2.0)",
   long_description='A simple, flexible, and powerful config reader for Python. Features include support for multiple formats (ini, xml, json, yaml), layering (default, environment, local), and load modes (implicit, explicit)',
   author='Phenicle',
   author_email='pheniclebeefheart@gmail.com',
   url="https://github.com/phenicle/cfgpy",
   packages=['cfgpy',],  #same as name
   install_requires=['configparser', 'xmltodict'], #external packages as dependencies
)
