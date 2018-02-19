# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


def _read_file(name, encoding='utf-8'):
    """
    Read the contents of a file.

    :param name: The name of the file in the current directory.
    :param encoding: The encoding of the file; defaults to utf-8.
    :return: The contents of the file.
    """
    with open(name, encoding=encoding) as f:
        return f.read()


setup(
    name='trawsate',
    version='0.0.1',
    description='Rotates AWS access keys used by Travis CI.',
    long_description=_read_file('README.rst'),
    license='MIT',
    url='https://github.com/gebn/trawsate',
    author='George Brighton',
    author_email='oss@gebn.co.uk',
    packages=find_packages(),
    zip_safe=True,
    install_requires=[
        'boto3>=1.5.31',
        'requests>=2.18.4'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': [
            'trawsate = trawsate.__main__:cli',
        ]
    }
)
