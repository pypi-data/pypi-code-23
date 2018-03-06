#! /usr/bin/env python


from setuptools import setup
setup(
    name='toro-element',
    version='1.1',
    author='Jerrick M Pua',
    author_email='jerrick.pua@toro.io',
    description='create element with markdown syntax',
    url='https://toro.io',
    py_modules=['toro-element'],
    install_requires=['Markdown>=2.0',]

)
