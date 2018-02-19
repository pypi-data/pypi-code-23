import os
from setuptools import setup, find_packages

import pypandoc

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = pypandoc.convert_file('README.md', 'rst', format='md')

setup(
    name='prettymatrix',
    version='0.1.2',
    packages=find_packages(),
    license='MIT',
    author='Samuel Bell',
    author_email='samueljamesbell@gmail.com',
    url='https://github.com/samueljamesbell/prettymatrix',
    description='Pretty printer for matrices and column vectors.',
    long_description=long_description,
    keywords='matrix matrices vector formatting string numpy',
    install_requires=['numpy'],
)
