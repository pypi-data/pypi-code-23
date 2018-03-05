"""

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # $ pip install logup
    name='logup',  # Required

    version='1.0.0',  # Required

    description='The LogUp SDK for Python',  # Required

    long_description=long_description,  # Optional

    url='https://github.com/logupinc/logup-sdk-python',  # Optional

    author='LogUp Inc.',  # Optional

    author_email='it@logup.co',  # Optional

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7'
    ],

    keywords='logup logup-sdk-python logup-python logup-sdk',  # Optional

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    license="Apache License 2.0",

    install_requires=['requests'],  # Optional

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/logupinc/logup-sdk-python/issues',
        'Source': 'https://github.com/logupinc/logup-sdk-python',
    },
)