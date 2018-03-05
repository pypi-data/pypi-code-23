# coding:utf-8
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'easyEEG',
    version = '0.8.2',
    keywords = ['experiment', 'eeg', 'analysis', 'analyzer', 'neuroscience'],
    description = 'Concise, agile, and flexible EEG toolbox',
    author = 'Jinbiao Yang',
    author_email='Jinbiao.Yang@mpi.nl',
    long_description=long_description,
    license = 'GPL License',
    packages = find_packages(),
    install_requires = ['numpy','pandas','scipy','matplotlib','statsmodels','seaborn','mne','permute','tqdm','ipdb'],

    include_package_data=True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3',
    ],
)
