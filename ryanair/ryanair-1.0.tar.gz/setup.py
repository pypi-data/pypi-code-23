from setuptools import setup
from setuptools import find_packages

packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

with open("readme.md", 'r') as f:
    long_description = f.read()

setup(
    name='ryanair',
    version='1.0',
    packages=packages,
    url='',
    license='',
    author='Creal',
    author_email='crealcode@gmail.com',
    description='Lightweight code to search for (round) flights, using: multiple arrival/departure airports, date range and day of week as input.',
    install_requires=['datetime','requests','pandas'],  # external packages as dependencies

)
