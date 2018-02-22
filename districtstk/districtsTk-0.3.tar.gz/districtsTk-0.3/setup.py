"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

setup(
    name='districtsTk',

    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='A script to check whether or not a point on earth is within a given district.',
    long_description=long_description,

    # The project's main homepage.
    url='https://hannover.freifunk.net',

    # Author details
    author='Aiyion and Raute from Freifunk Hannover',
    author_email='dev@hannover.freifunk.net',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='district localisation geocoordinates',
    py_modules=["districtsTk"],
)
