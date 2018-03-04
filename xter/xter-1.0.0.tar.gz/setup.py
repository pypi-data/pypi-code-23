from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='xter',
    version='1.0.0',
    description='Executor for commands from the Commander API.',
    author='www.itscoding.ch',
    author_email='simon.d.mueller@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='commander client, executor itscoding',
    packages=find_packages(exclude=['test','examples']),
    install_requires=['requests','pprint'],
)