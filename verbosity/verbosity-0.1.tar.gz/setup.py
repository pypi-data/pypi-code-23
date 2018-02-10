# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='verbosity',
    packages=['verbosity'],  # this must be the same as the name above
    version='0.1',
    description='Add verbosity options with argparse and logging',
    author='Justin S. Peavey',
    author_email='jspvpypi@twinleaf.xyz',
    url='https://github.com/jspv/verbosity',
    download_url='https://github.com/jspv/verbosity/archive/0.1.tar.gz',
    keywords=['argparse', 'logging'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3'
)
