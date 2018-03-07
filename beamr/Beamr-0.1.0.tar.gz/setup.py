'''
Created on 6 Mar 2018

@author: Teofor G Nistor
'''
from setuptools import setup, find_packages
from beamr.cli import arg

setup(**arg, packages=find_packages())
