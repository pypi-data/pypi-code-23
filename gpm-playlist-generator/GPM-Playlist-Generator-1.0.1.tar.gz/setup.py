#!/usr/bin/env python

from setuptools import find_packages, setup
import pypandoc

about = {}
with open('gpmplgen/__version__.py') as f:
    exec(f.read(), about)

setup(name='GPM-Playlist-Generator',
      version=about['__version__'],
      description='Google Play Music - Playlist Generator',
      long_description = pypandoc.convert_file('README.md', 'rst', format='markdown_github'),
      author='Hugo Haas',
      author_email='hugoh@hugoh.net',
      url='https://gitlab.com/hugoh/gpm-playlistgen',
      packages=find_packages(exclude=('tests',)),
      scripts=[
          'scripts/gpm-playlistgen.py'
      ],
      install_requires=[
          'gmusicapi',
          'pyyaml'
      ],
      keywords=['google music', 'google play music', 'playlist', 'playlist generator'],
      classifiers=[
          'Environment :: Console',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Intended Audience :: End Users/Desktop',
          'Topic :: Multimedia :: Sound/Audio',
      ]
      )
