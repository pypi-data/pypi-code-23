
from setuptools import setup, find_packages

import objects_query

setup(
    name='objects_query',
    version=objects_query.__version__,
    author=objects_query.__author__,
    author_email=objects_query.__email__,
    url='https://bitbucket.org/blins/objects_query/',
    packages=find_packages(),
)