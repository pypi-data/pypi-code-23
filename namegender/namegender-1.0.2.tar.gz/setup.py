""" Predict the gender of a name based on statistical data

@copyright: 2018 samuorous <samuorous@gmail.com>
@licence: GPLv3
"""
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README.md file
try:
    import pypandoc
    import re
    long_description = pypandoc.convert(path.join(here, 'README.md'), "rst")
except:
    long_description = ""

setup(
    name='namegender',
    version='1.0.2',
    description='Predict the gender of a name based on statistic data',
    long_description=long_description,
    url='https://github.com/samuorous/namegender',
    author='Samuorous',
    author_email='samuorous@gmail.com',
    license='GPLv3',
    keywords='name gender prediction',
    packages=find_packages(),
    package_data={
        'namegender': ['data/gender_name_mapping.txt'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/samuorous/namegender/issues',
        'Source': 'https://github.com/samuorous/namegender',
    },
)
