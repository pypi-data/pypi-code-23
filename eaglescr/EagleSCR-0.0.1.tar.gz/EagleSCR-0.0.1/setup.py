#!/usr/bin/env python

from distutils.core import setup

setup(
      name = 'EagleSCR'
   ,  version = '0.0.1'
   ,  description = 'Parser for the Eagle scripting language'
   ,  long_description = """Parser and partial evaluator for the scripting \
   language used by AutoDesk's Eagle CAD software."""
   ,  author = 'Derp Ston'
   ,  author_email = 'derpston+pypi@sleepygeek.org'
   ,  url = 'https://github.com/derpston/pyEagleSCR'
   ,  package_dir = {'': 'src'}
   )

