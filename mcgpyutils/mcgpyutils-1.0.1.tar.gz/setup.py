from setuptools import setup, find_packages
from codecs import open
from os import path
import sys
import pypandoc
import mcgpyutils

if sys.version_info < (3, 6):
    print('mcgpyutils requires python3 version >= 3.6.')
    sys.exit(1)

version = mcgpyutils.__version__
long_description = pypandoc.convert('README.md', 'rst')

setup(
    name='mcgpyutils',
    version=version,
    description='Common Python utilities used at MCG Strategic',
    long_description=long_description,
    url='https://www.mcgstrategic.com',
    author='MCG Strategic',
    author_email='support@mcgstrategic.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'requests',
        'slacker',
        'google-api-python-client'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
)
