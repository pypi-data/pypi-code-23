from os import path
from setuptools import setup, find_packages
from bglogs import __version__


directory = path.dirname(path.abspath(__file__))
with open(path.join(directory, 'requirements.txt')) as f:
    required = f.read().splitlines()


setup(
    name='bglogs',
    version=__version__,
    description='BBGLab tool',
    packages=find_packages(),
    install_requires=required
)