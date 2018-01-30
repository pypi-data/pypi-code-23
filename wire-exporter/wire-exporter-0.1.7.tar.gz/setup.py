import os.path

import codecs
from setuptools import setup, find_packages

from wire_exporter import __PROJECT__, __VERSION__

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), encoding='utf-8') as h:
    long_description = h.read()

required = [
    'click>=6.7',
    'prometheus_client>=0.1.1',
    'netifaces>=0.10.6',
    'pyyaml>=3.12',
    'pyshark>=0.3.7.11'
]

setup(
    name=__PROJECT__,
    version=__VERSION__,
    description='Exports statistics about wire traffic in Prometheus exporter format',
    long_description=long_description,
    author='David Bauer',
    author_email='david@darmstadt.freifunk.net',
    url='https://www.github.com/blocktrron/wire-exporter',
    license='MIT',
    install_requires=required,
    packages=find_packages(),
    package_data={'wire_exporter': ['filters/*.yaml']},
    entry_points={
        'console_scripts': ['wire-exporter=wire_exporter:cli.run']
    },
)
