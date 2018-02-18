"""Plex syncing"""
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

exec(open("plex_sync/version.py").read())

setup(name='plex-sync',
      version=__version__,
      license="MIT",
      url="https://github.com/d1vanloon/python-plex-sync",
      author="David Van Loon",
      author_email="david+pypi@davidvanloon.me",
      description='Sync playback status between Plex servers',
      long_description=long_description,
      install_requires=[
          'requests',
          'tqdm',
          'websocket-client'
      ],
      packages=find_packages(),
      python_requires='>=3.5',
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'plex-sync=plex_sync.sync:main'
          ]
      })
