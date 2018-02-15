"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='zped',
    version='0.1.0',  # Required
    description='A poorly-architected event dispatcher that does magic and lets you do terrible things',  # Required
    long_description=long_description,  # Optional
    url='https://github.com/zoidbb/zped',  # Optional
    author='Ber Zoidberg',  # Optional
    author_email='ber@zoidplex.net',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='event dispatcher',
    scripts=['zped.py'],
    py_modules=['zped']
)

