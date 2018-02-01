"""
Setup for Docs Configuration
"""
from setuptools import setup, find_packages

from docs_conf import __author__
from docs_conf import __version__


with open('requirements.txt') as f:
    install_reqs = f.read().splitlines()


setup(
    name='lfdocs_conf',
    packages=['docs_conf'],
    version=__version__,
    author=__author__,
    author_email="releng@linuxfoundation.org",
    url="https://gerrit.linuxfoundation.org/docs-conf",
    package_data={
        'docs_conf': ['defaults/*']
    },
    install_requires=install_reqs
)
