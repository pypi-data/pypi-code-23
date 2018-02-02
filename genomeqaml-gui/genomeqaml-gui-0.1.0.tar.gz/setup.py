#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="genomeqaml-gui",
    version="0.1.0",
    packages=find_packages(),
    author="Forest Dussault",
    author_email="forest.dussault@inspection.gc.ca",
    url="https://github.com/forestdussault/GenomeQAML_GUI",
    scripts=['qamlgui.py'],
    install_requires=['GenomeQAML']
)