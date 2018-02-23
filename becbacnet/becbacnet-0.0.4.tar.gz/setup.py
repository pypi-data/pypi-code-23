""" Setup file.
"""
import os
from setuptools import setup

setup(name='becbacnet',
    version="0.0.4",
    description='client for becbacnet API',
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords="web services API",
    author='Graeme Stuart',
    author_email='ggstuart@gmail.com',
    url='',
    py_modules=['becbacnet'],
    zip_safe=True,
    install_requires=[
        'requests',
    ],
)
