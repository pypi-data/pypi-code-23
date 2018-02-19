"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import os

from setuptools import setup, find_packages

# pylint: disable=redefined-builtin

here = os.path.abspath(os.path.dirname(__file__))  # pylint: disable=invalid-name

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()  # pylint: disable=invalid-name

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='reconnecting_ftp',
    version='1.0.0',
    description='Reconnecting FTP client',
    long_description=long_description,
    url='https://github.com/mristin/reonnecting_ftp',
    author='Marko Ristin',
    author_email='marko.ristin@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='ftplib reconnect retry robust',
    python_requires='>=3.5',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[],
    extras_require={
        'test': ['pyftpdlib'],
        'dev': ['mypy==0.560', 'pylint==1.8.2', 'yapf==0.20.2']
    },
    py_modules=['reconnecting_ftp'])
