from setuptools import setup
import sys
from os import path
from codecs import open

if sys.version_info < (3, 0):
    raise RuntimeError("Python 3+ required for asciiRyver to work.")

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='asciiRyver',
    version='1.0a1',
    description='Ryver for the terminal',
    long_description=long_description,
    url='https://github.com/lillyjsm/asciiRyver',
    author='Jake Lilly',
    author_email='Lillyjsm@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Chat'

    ],
    packages=['asciiRyver'],
    install_requires=[
        'requests==2.18.4',
        'websocket-client==0.46.0',
        'asciimatics==1.9.0'
    ],
    entry_points={
        'console_scripts': [
            'asciiRyver=asciiRyver.__main__:main',
        ],
    },
)