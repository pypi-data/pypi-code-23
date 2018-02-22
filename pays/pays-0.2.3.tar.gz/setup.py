"""
Setup

Usage :
* `python setup.py test -> unittests
"""

from setuptools import setup, find_packages

try:
    from pypandoc import convert
    README = convert('README.md', 'rst')
except ImportError:
    print('!!! pandoc manquant, la description sera en markdown')
    README = open('README.md').read()

with open('requirements.in') as requirements:
    REQUIRES = requirements.read().splitlines()

setup(
    name='pays',
    version='0.2.3',  # géré par bumpversion
    description='Liste de pays en dict',
    author='Canarduck',
    author_email='renaud@canarduck.com',
    url='https://gitlab.com/canarduck/pays',
    keywords='countries iso3166',
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=README,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    test_suite='tests')
