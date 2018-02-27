# -*- coding: utf-8 -*-
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "sonicparanoid.inpyranoid_c",
        ["sonicparanoid/inpyranoid_c.pyx"],
        include_dirs=[numpy.get_include()], # not needed for fftw unless it is installed in an unusual place
        #libraries=['fftw3', 'fftw3f', 'fftw3l', 'fftw3_threads', 'fftw3f_threads', 'fftw3l_threads'],
        #library_dirs=['/some/path/to/include/'], # not needed for fftw unless it is installed in an unusual place
    ),
    Extension(
        "sonicparanoid.mmseqs_parser_c",
        ["sonicparanoid/mmseqs_parser_c.pyx"],
        include_dirs=[numpy.get_include()], # not needed for fftw unless it is installed in an unusual place
        #libraries=['fftw3', 'fftw3f', 'fftw3l', 'fftw3_threads', 'fftw3f_threads', 'fftw3l_threads'],
        #library_dirs=['/some/path/to/include/'], # not needed for fftw unless it is installed in an unusual place
    ),
]

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# constant variables to be used inside the setup function
LICENSE = 'GNU GENERAL PUBLIC LICENSE, Version 3.0 (GPLv3)'


# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name='sonicparanoid',  # Required
    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1.0',  # Required
    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='SonicParanoid: fast, easy, and accurate orthology inference',  # Required
    long_description=long_description,  # Optional
    url='http://iwasakilab.bs.s.u-tokyo.ac.jp/sonicparanoid/',  # Optional
    # This should be your name or the name of the organization which owns the
    # project.
    author='Salvatore Cosentino',  # Optional
    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='salvo@gmail.com',  # Optional
    # license
    license=LICENSE,
    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[  # Optional
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='bioinformatic inparanoid orthology_inference phylogeny evolution orthology',  # Optional
    # external to be compiled
    ext_modules = cythonize(extensions, compiler_directives={'language_level': 3}),
    #package_dir={'': 'sonicparanoid'},
    package_dir={'sonicparanoid': 'sonicparanoid/'},
    #packages = find_packages('sonicparanoid'),
    #packages = find_packages('sonicparanoid'),
    packages = ['sonicparanoid',],
    install_requires=['numpy>=1.14.0', 'pandas>=0.22.0', 'cython>=0.27.0', 'sh>=1.12.14', 'setuptools>=24.2.0', 'pip>=9.0.1'], # specify minimum version
    # required python version
    python_requires='>=3.5, <3.7',
    include_package_data=True,
    package_data={'sonicparanoid': ['config.json', 'example/test_output/*', 'example/test_input/*', 'mmseqs2_src/*', 'quick_multi_paranoid/*', 'bin/README.txt']
                },  # Optional

    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'sonicparanoid = sonicparanoid.sonic_paranoid:main',
            'sonicparanoid-get-mmseqs2 = sonicparanoid.get_mmseqs2:main',
            'sonicparanoid-set-mmseqs2 = sonicparanoid.set_mmseqs2:main',
            'sonicparanoid-get-test-data = sonicparanoid.get_test_data:main',
        ],
    },

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={  # Optional
        'Source': 'https://bitbucket.org/salvocos/sonicparanoid',
    },
)
