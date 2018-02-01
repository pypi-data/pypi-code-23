from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name = 'tamcolors',
    version = '0.2.0',  
    description = 'Output & input in color on terminal.',
    long_description = long_description,
    author = 'Charles McMarrow',
    platforms = ['any'],
    license = 'GPLv3',
    classifiers=[
        'Natural Language :: English',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        
        'Topic :: Terminals',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        
        'Programming Language :: Python :: 3.6',
        'Programming Language :: C++'
    ],
    python_requires='~=3.6',
    
    keywords='tammy color colors terminal',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={  
        'tamcolors': ['_tamcolors.cp36-win_amd64.pyd', '_tamcolors.cp36-win32.pyd', 'LICENSE.txt']
    }
)
