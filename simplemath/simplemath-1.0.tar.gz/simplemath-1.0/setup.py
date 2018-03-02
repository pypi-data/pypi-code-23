

from setuptools import setup, find_packages
from os import path
from codecs import open

'''here = path.adspath(path.dirname(_file_)
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()'''
 

setup(
    name='simplemath',
    version='1.0',
    description='A simple calculation package',
    author='krushithreddy',
    author_email='krushithreddy567@gmail.com',
    url='https://github.com/krushithreddy/simplemath.git',
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords = 'math',
    packages=find_packages(exclude=['tests']),
    
)
