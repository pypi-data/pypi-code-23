#!/usr/bin/env python

from distutils.core import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


setup(
      name = 'EagleSCR'
   ,  version = '0.1.0'
   ,  description = 'Parser for the Eagle scripting language'
   ,  long_description = read_md('README.md')
   ,  author = 'Derp Ston'
   ,  author_email = 'derpston+pypi@sleepygeek.org'
   ,  url = 'https://github.com/derpston/pyEagleSCR'
   ,  packages = ['eaglescr']
   )

