from setuptools import setup, find_packages

setup(
    # Application name:
    name="corpussearch",

    # Version number (initial):
    version="0.0.2",

    # Application author details:
    author="Malte Vogl",
    author_email="mvogl@mpiwg-berlin.mpg.de",

    # Packages
    packages=["corpussearch"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/corpussearch/",

    license="LICENSE.txt",
    description="Tools for loading and analyzing large text corpora.",

    long_description=open("README.md").read(),

    classifiers=[
        # How mature is this project?
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Indexing',
        # Pick your license as you wish
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        # Specify the Python versions you support here.
        'Programming Language :: Python :: 3',
    ],
    project_urls={
        'Source': 'https://github.com/TOPOI-DH/corpussearch/',
        'Tracker': 'https://github.com/TOPOI-DH/corpussearch/issues',
        'Download': 'https://github.com/TOPOI-DH/corpussearch/archive/0.0.2.tar.gz',
    },

    python_requires='>=3',

    # Dependent packages (distributions)
    install_requires=[
        "pandas",
    ],
)
