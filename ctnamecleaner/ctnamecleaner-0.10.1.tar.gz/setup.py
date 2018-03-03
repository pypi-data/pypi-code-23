""" Setup script for package """

#!/usr/bin/env python2

from setuptools import setup

try:
    setup(author="Jake Kara",
          author_email="jake@jakekara.com",
          url="https://github.com/jakekara/ctnamecleaner-py",
          download_url="https://pypi.python.org/pypi/ctnamecleaner/",
          name="ctnamecleaner",
          description="Replace village names and commonly-misspelled Connecticut town names with real town/city names.",
          long_description=open("README.md").read(),
          version="0.10.1",
          install_requires=["pandas","argparse"],
          packages=["ctlookup"],
          package_data={"ctlookup":["data/ctnamecleaner.csv"]},
          scripts=["ctclean"],
          license="GPL-3.0")
except:
    print ":( Error occurred: " + str(e)
    
