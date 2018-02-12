"""
A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from codecs import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='kdu-jp2',

    version='1.1',

    description='Batch conversion to JP2 using kdu_compress',
    long_description=long_description,

    url='https://github.com/kingsdigitallab/kdu-jp2',

    author='King\'s Digital Lab',
    author_email='kdl-info@kcl.ac.uk',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Utilities',
    ],

    keywords='jp2 conversion kdu kakadu kdu_compress batch',

      scripts=['bin/imgtojp2'],
    packages=['kdu_jp2'],

    include_package_data=True,

    install_requires=['progressbar33'],
)
