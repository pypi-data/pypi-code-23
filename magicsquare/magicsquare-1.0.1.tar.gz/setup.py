import os
import sys

from setuptools import setup, find_packages

PROJECT_NAME = 'MagicSquare'
MODULE_NAME = 'magicsquare'

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python3 setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

setup(
    name='magicsquare',
    version='1.0.1',

    author='JuneSunshine',
    author_email='ljygeek@gmail.com',

    description='Magic Square allows you to generate magic square at any length in python',
    long_description='Magic Square allows you to generate magic square at any length in python',
    keywords='magicsquare python3 package',

    url='https://github.com/JuneSunshine/Magic_Square',
    license="MIT Licence",

    platforms='all',

    packages=find_packages(),
    include_package_data=True,

)