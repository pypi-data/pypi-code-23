"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from os import path
from codecs import open as codecs_open
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with codecs_open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(

    name='YetAnotherPyOptional',
    version='0.1.1',
    description='An optional-api for python',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/erikthorstenson/python-optional',
    author='Erik Lilljequist',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Return values ' 'Declarative programming ' 'No NPE ',
    packages=find_packages(exclude=['tests']),
    install_requires=[],
)
