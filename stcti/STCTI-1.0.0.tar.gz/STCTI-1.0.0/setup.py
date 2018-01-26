"""A setup tools based setup module.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='STCTI',
    version='1.0.0',
    description='A CTI reliability and risk analysis project',
    long_description=long_description,
    url='https://github.com/gongsh93/STCTI',
    author='Seonghyeon Gong',
    author_email='gongsh@seoultech.ac.kr',
    license='MIT',
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Security ',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='cyber threat intelligence',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
    extras_requires={},
    package_data={},
    entry_points={},
)
