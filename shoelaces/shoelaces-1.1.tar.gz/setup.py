#from distutils.core import setup
from setuptools import setup, find_packages
setup(
  name = 'shoelaces',
  packages = find_packages(),
  version = '1.1',
  description = 'An open source program for processsing ribosome profiling data',
  author = 'Åsmund Birkeland',
  author_email = 'asmund.birkeland@uib.no',
  url = 'https://bitbucket.org/valenlab/shoelaces',
  download_url = 'https://bitbucket.org/valenlab/shoelaces/archive/1.1.tar.gz',
  keywords = ['python', 'bioinformatics', 'gui', 'ribosome profiling'], 
  classifiers = [],
  package_data={
        'shoelaces': [
            'resources/logo.png',
            'resources/save-icon.png',
        ]
    },
  install_requires=[
        'pysam',
        'numpy',
        'pyqt5',
        'pyopengl',
    ],
    entry_points={
        'console_scripts': ['shoelaces=shoelaces.main:cli']
    },
)