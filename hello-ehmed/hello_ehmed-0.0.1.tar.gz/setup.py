#!/usr/bin/env python3
from setuptools import setup
from hello import __version__

with open('README.rst') as f:
    readme = f.read()
with open('CHANGES.rst') as f:
    changes = f.read()

setup(
    name='hello_ehmed',
    version=__version__,
    description='describe please',
    long_description=readme + '\n\n' + changes,
    author='Ehmed Kino',
    author_email='ehmadaff@gmail.com',
    url='https://github.com/Ehmed-kino/wh_lilgarb.git',
    py_modules=['hello', ],
    license='MIT',
    entry_points={
        'console_scripts': ['hello=hello:main']
    }
)
