import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='psycopg2-contextmanager',
    version='1.0.3',
    packages=['psycopg2_contextmanager'],
    license='MIT',
    include_package_data=True,
    description='Minimal psycopg2 wrapper for easier interfacing with databases',
    long_description=README,
    url='https://www.gridsmart.com/',
    author='Devon Campbell',
    author_email='devon.campbell@gridsmart.com',
    install_requires=['psycopg2']
)
