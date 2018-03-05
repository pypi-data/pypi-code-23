import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pr-creator",
    version="0.0.3",
    author="Ben Warren",
    author_email="bwarren@eab.com",
    description=("Git lifestyle utility for NaviGuide"),
    license="BSD",
    keywords="happy dev",
    url="https://github.com/bwarren2/create-prs",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points={
        "console_scripts": [
            "create-prs=pr_creator.main:main",
        ]
    },
    install_requires=[
        'requests>=2.18.4',
    ],
)
