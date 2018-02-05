#!/usr/bin/env python
from setuptools import setup
import os
import springserve

dir = os.path.split(os.path.abspath(__file__))[0]


DESCRIPTION = "API Library for video.springserve.com"
LONG_DESCRIPTION = """Springserve is a video adserver, and this library allows you
to interface with its api to do read/write and reporting requests """
URL = 'http://www.springserve.com'
DOWNLOAD_URL = ''
CLASSIFIERS = ['Development Status :: 4 - Beta',     
               'Programming Language :: Python',
               'Programming Language :: Python :: 2',
               'Programming Language :: Python :: 3'
              ]
EMAIL = ''
SETUP_ARGS = {}
REQUIRES = ['requests>=2.0.0', 'requests_oauthlib>=0.4.0',
            'link>=0.3.1','xmltodict', 'pandas', 'six' ]

# write out the version file so we can keep track on what version the built
# package is

# call setup so it can build the package
setup(name=springserve.__title__,
      version=springserve.__version__,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      license=springserve.__license__,
      maintainer_email=EMAIL,
      maintainer=springserve.__author__,
      url=URL,
      packages=['springserve'],
      install_requires = REQUIRES,
      #data_files = DATA_FILES,
      classifiers=CLASSIFIERS,
      **SETUP_ARGS)
