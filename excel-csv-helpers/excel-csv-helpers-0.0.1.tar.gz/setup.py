import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "excel-csv-helpers",
    version = "0.0.1",
    author = "Rizwan Hameed",
    author_email = "rizwanbutt314@gmail.com",
    description = ("This package will help you for reading/writing excel or csv "
                   "files with multiple options"),
    license = "MIT",
    keywords = "Excel/CSV Reader Writer",
    url = "http://packages.python.org/excel-csv-helpers",
    packages=['helpers', 'tests'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
    ],
)