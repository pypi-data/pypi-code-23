"""`pycfgr` | Easy config reader with `.yaml` and `.json` out-of-the box support

*Pycfgr* provides easy means of handling `.yaml` and `.json` based configs.
with support of interpolation of values based on config fields.
It is inspired by a great `config` package for **R** language by *RStudio*.
"""

from os import path
from codecs import open     #pylint: disable=W0622
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use consistent encoding
# Import version
from pycfgr import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pycfgr',

    # Versions should comply with PEP440. For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html

    version=__version__,

    description="Easy config reader with .yaml and .json out-of-the box support",
    long_description=long_description,

    # The project's main homepage
    url='https://github.com/sztal/pycfgr',

    # Author details
    author='Szymon Talaga',
    author_email='stalaga@protonmail.com',

    # Choose your licence
    license='MIT',

    # Dependencies
    install_requires=[
        'PyYAML>=3.12,<4.0',
        'pytest>=3.4.0'
    ],

    # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project?
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Intended audience
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        # License
        'License :: OSI Approved :: MIT License',
    ],

    # What does your project relate to?
    keywords='pycfgr config cfg conf configuration yaml json',

    # You can just specify the packages manually here if your project is simple.
    packages=find_packages(exclude = ['contrib', 'docs', 'tests'])

)
