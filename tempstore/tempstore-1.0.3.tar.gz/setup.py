import os
from setuptools import setup, find_packages


def read(fname):
    """Reads the README file."""
    with open(os.path.join(os.path.dirname(__file__), fname), 'r') as fp:
        return fp.read()


setup(
    name="tempstore",
    version="1.0.3",
    author="Ryan Richholt",
    website="https://github.com/ryanrichholt/tempstore",
    description="A simple container for handling multiple tempfiles",
    long_description=read('README.rst'),
    keywords="temp tempfile tempdir",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
