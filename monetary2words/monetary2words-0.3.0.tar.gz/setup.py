# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name="monetary2words",
    version='0.3.0',
    author="Focusate",
    author_email="dev@focusate.eu",
    url='https://github.com/focusate/extra-tools',
    license='MIT',
    long_description=open('README.rst').read(),
    py_modules=['monetary2words', ],
    install_requires=[
        'float2words',
    ],
)
