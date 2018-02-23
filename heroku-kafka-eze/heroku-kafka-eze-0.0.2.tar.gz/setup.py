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
    version='0.0.2',            # Update the version number for new releases
    name='heroku-kafka-eze',        # This is the name of your PyPI-package.
    description='Python kafka package for use with heroku\'s kafka. You\'ll only need your heroku api key and app name',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    url='https://github.com/masalomon01/heroku-kafka-eze',
    author='MarSal',
    keywords='heroku, kafka',
    author_email='salermom@gmail.com',
    license='MIT',
    py_modules=["heroku_kafka_eze"],
    install_requires=[
        'kafka-python==1.3.5', 
        'heroku3==3.3.0'
    ]
)