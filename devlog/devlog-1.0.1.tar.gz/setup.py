from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='devlog',
    version='1.0.1',
    description='A simple command line developer log',
    long_description=long_description,
    author='Kacha Mukabe',
    author_email='kmukabe@gmail.com',
    url='https://www.github.com/kachamukabe/devlog',
    license='MIT',
    # download_url='https://github.com/kachaMukabe/devlog/archive/v1.0.tar.gz',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    keywords='development blogging',
    python_requires='>=3',
    classifiers=[
    ],
    entry_points={
        'console_scripts':[
            'devlog=devlog:main',
        ],
    },
)
