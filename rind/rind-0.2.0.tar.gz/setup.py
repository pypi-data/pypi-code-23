import io
import os

from setuptools import setup

NAME = 'rind'

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

about = {}
with open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)

setup(
    name=NAME,
    version=about['__version__'],
    author='Jonathan Moss',
    author_email='jmoss@commoncode.io',
    url='https://github.com/a-musing-moose/rind',
    license='MIT',
    packages=[NAME],
    install_requires=[
        'click~=6.7',
        'docker~=2.7.0',
        'pyyaml~=3.12',
        'dockerpty',
    ],
    description='Run in Docker',
    long_description=long_description,
    classifiers=(
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6',
    ),
    entry_points={
        'console_scripts': ['rind=rind.cli:run'],
    })
