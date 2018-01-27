"""Tesults API library module.

See:
https://www.tesults.com
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

setup(
    name='tesults',
    version='1.2.0',
    description='Tesults API library',
    long_description='Tesults API library for uploading test results to Tesults in your python application.',
    url='https://www.tesults.com',
    author='Tesults',
    author_email='support@tesults.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'requests',
        'boto3'
    ],
    keywords='tesults test results automation automated dashboard reporting',
    py_modules=['tesults']
)