"""A setuptools based setup module.
See:
https://packaging.python.org/tutorials/distributing-packages/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pymeda',
    version='0.0.3',
    description='Matrix Exploratory Data Analysis',
    url='https://github.com/neurodata-nomads/pymeda',
    download_url='https://github.com/neurodata/ndmg/tarball/0.0.3',
    author='Jaewon Chung',
    author_email='j1c@jhu.edu',
    license='MIT',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],
    keywords='data visualization analysis',
    packages=['pymeda'],  # Required
    install_requires=[
        'colorlover==0.2.1', 'jupyter==1.0.0', 'numpy==1.13.1',
        'pandas==0.21.0', 'plotly==2.2.3', 'scipy==1.0.0', 'redlemur==0.10.0',
        'scikit-learn==0.19.1', 'knor', 'cython', 'boto3==1.4.7',
        'nilearn==0.4.0', 'matplotlib==2.1.0', 'nose', 'imageio'
    ],

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    # If using Python 2.6 or earlier, then these have to be included in
    # MANIFEST.in as well.
    package_data={  # Optional
        'pymeda': ['templates/*.html'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    #
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],  # Optional
    include_package_data=True)
