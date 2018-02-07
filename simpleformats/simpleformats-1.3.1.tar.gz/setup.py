from distutils.core import setup

setup(
    name = 'simpleformats',
    version = '1.3.1',
    description = 'Simple formatted-text file parsing/creation library',
    author = 'Jesters Ghost',
    author_email = 'jestersghost@gmail.com',
    url = 'https://bitbucket.org/jestersghost/simpleformats',
    requires = ['ctxlogger', 'openpyxl', 'xmltodict'],
    package_dir = {'simpleformats': '.'},
    packages = [
        'simpleformats',
        'simpleformats.batch',
        'simpleformats.tests',
    ],
    package_data = {'simpleformats.tests': ['types.xlsx']},
)
