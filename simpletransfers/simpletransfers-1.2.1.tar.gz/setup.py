from __future__ import print_function, unicode_literals
from setuptools import setup, find_packages

setup(
    name = 'simpletransfers',
    version = '1.2.1',
    description = 'Simple file transfer library',
    author = 'Jesters Ghost',
    author_email = 'jestersghost@gmail.com',
    url = 'https://bitbucket.org/jestersghost/simpletransfers',
    requires = ['ctxlogger'],
    package_dir = {'simpletransfers': 'simpletransfers'},
    packages = find_packages(),
    package_data = {'simpletransfers.tests': ['one.txt', 'test.zip']},
    tests_require = ['ctxlogger', 'stubserver' ,'localmail', 'twisted<=13.0'],
    test_suite = 'simpletransfers.tests',
)
