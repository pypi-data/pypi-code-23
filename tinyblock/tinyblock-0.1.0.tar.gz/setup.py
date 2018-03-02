
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='tinyblock',
    version='0.1.0',
    description='A simple blockchain package.',
    long_description=open("README.rst").read(),
    url='https://github.com/zshvvhm/tinyblock',
    author='zshvvhm',
    author_email='zshvvhm95@gmail.com',
    license='MIT',
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    classifiers=[
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='simple tiny blockchain',
    packages=['tinyblock'],
    project_urls={
        'Bug Reports': 'https://github.com/zshvvhm/tinyblock/issues',
        'Source': 'https://github.com/zshvvhm/tinyblock',
    },
)