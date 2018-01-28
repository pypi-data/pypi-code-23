from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-raise',
    version='0.0.7',
    description='Raise money from pledges',
    long_description=long_description,
    url='https://github.com/AvocadoCoop/django-raise',
    author='Avocado Co-op',
    author_email='albert@avocado.coop',
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={},
)
