from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="poly-escape-graph",
    version="3.3",
    description='Python graph oriented micro services network in order to implement a scalable plugins architecture',
    long_description=long_description,
    author='PEE',
    url='https://mjollnir.unice.fr/bitbucket/scm/pee/private.git',
    python_requires='>=3.6, <4',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['flask', 'flask_sqlalchemy', 'requests', 'urllib3'],
    license="Unlicense"
)
