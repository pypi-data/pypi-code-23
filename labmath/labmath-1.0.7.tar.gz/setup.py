#! /usr/bin/env python3

from setuptools import setup # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'labmath/DESCRIPTION.rst'), encoding='utf-8') as f: long_description = f.read()

setup(
    name='labmath',
    version='1.0.7',
    description='Module for basic math in the general vicinity of computational number theory',
    long_description=long_description,
    url='https://pypi.python.org/pypi/labmath',
    author='lucasbrown.cit',
    author_email='lucasbrown.cit@gmail.com',
    license='MIT',
    keywords="math mathematics computational number theory integer factoring factorization primes prime numbers legendre symbol jacobi symbol kronecker symbol elliptic curve method bpsw miller rabin quadratic frobenius prp sprp lprp slprp xslprp primality testing linear recurrences lucas sequences modular square root generalized Pell equations divisor counting function euler's totient function mobius function möbius function continued fractions partitions stormer's theorem størmer's theorem smooth numbers Dirichlet convolution",
    packages=['labmath'],
    python_requires='>=3',
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: Free For Educational Use',
        'License :: Free For Home Use',
        'License :: Free for non-commercial use',
        'License :: Freely Distributable',
        'License :: Freeware',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries',
    ],
)

