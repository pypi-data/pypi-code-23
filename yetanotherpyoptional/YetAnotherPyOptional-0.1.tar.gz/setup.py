"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(

    name='YetAnotherPyOptional',  # Required

    version='0.1',  # Required

    description='An optional-api for python',  # Required

    url='https://github.com/erikthorstenson/python-optional',  # Optional

    author='Erik Lilljequist',  # Optional

    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='Return values' 'Declarative programming' 'No NPE',  # Optional

    py_modules=["Optional/src/optional.py"],

    install_requires=[],  # Optional
)
