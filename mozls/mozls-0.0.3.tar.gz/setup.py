import codecs
import os.path

from setuptools import setup, find_packages

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), encoding='utf-8') as h:
    long_description = h.read()

setup(
    name='mozls',
    version='0.0.3',
    description='Wrapper for the Mozilla Location Service API',
    long_description=long_description,
    author='David Bauer',
    author_email='david@darmstadt.freifunk.net',
    url='https://www.github.com/blocktrron/mozls',
    license='AGPLv3',
    install_requires=[
        "click",
        "requests", ],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['mls-locate=mozls:cli.run']
    },
)
