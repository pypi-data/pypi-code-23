from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="extractcontent3",
    version="0.0.2",
    description="ExtractContent for Python 3",
    long_description=long_description,
    license="BSD 2-Clause",
    url="https://github.com/kanjirz50/python-extractcontent3",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=[],
    dependency_links=[],
    python_requires='~=3.3',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
    ],
)
