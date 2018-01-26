import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="timmytimer",
    description='minimal timer wrapper with print or log',
    long_description = read('README.md'),
    version="0.2",
    url='https://github.com/hvgab/timmytimer',
    author='Henrik V. Gabrielsen',
    author_email='henrik.v.gabrielsen+timmytimer@gmail.com',
    license='MIT',
    packages=['timmytimer'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'
        ],
    )
