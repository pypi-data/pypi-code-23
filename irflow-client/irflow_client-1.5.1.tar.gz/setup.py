""" IR-Flow Client setup.py"""

from codecs import open
from setuptools import setup
import os

with open('requirements.txt') as f:
    base_requirements = f.read().splitlines()

with open('requirements-dev.txt') as f:
    dev_requirements = f.read().splitlines()

# Absolute repo path
here = os.path.abspath(os.path.dirname(__file__))

about = {}

with open(os.path.join(here, "irflow_client", '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    maintainer='Syncurity Corp.',
    maintainer_email='support@syncurity.net',
    keywords='Syncurity syncurity IR-Flow ir-flow irflow security incident response',
    license=about['__license__'],
    packages=['irflow_client'],
    install_requires=base_requirements,
    extras_require={
        'dev': [
            dev_requirements
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
    ]
)
