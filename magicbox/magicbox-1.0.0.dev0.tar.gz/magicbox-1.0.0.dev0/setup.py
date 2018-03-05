import re
import sys

if sys.version_info < (3, 6):
    sys.exit("Sorry, only Python 3.6 or above is supported")

from pathlib import Path

from setuptools import setup, find_packages


version = '1.0.0.dev0'
name = 'magicbox'
release = ''

author = 'Anton Shurpin'


setup(
    name=name,
    version=version,
    url='https://github.com/SlamJam/magixbox',
    license='Apache 2.0',
    author=author,
    author_email='anton.shurpin@gmail.com',
    description='Toolbox for rapid services prototyping',
    platforms='any',

    packages=find_packages(),

    zip_safe=True,
)
