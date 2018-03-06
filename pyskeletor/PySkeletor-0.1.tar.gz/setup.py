"""A setuptools based setup module.
Ref: https://github.com/pypa/sampleproject
"""
import codecs
from os import path

from setuptools import find_packages, setup

HERE = path.abspath(path.dirname(__file__))
with codecs.open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='PySkeletor',  # Required
    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    version='0.1',  # Required

    description='A fairly complete Python boilerplate project',  # Required
    long_description=LONG_DESCRIPTION,  # Optional
    url='https://github.com/rdhushyanth/Skeletor',  # Optional
    author='Dhushyanth Ramasamy',  # Optional
    author_email='pypi@dhushyanth.com',  # Optional

    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    packages=find_packages('src', exclude=['contrib', 'docs', 'tests'], ),  # Required
    package_dir={'': 'src'},
    install_requires=['click'],  # Optional
    setup_requires=['pytest-runner'], # Optional
    tests_require=['pytest'], # Optional
    entry_points={  # Optional
        'console_scripts': [
            'skeletor=skeletor.cli:main',
        ],
    },


)
