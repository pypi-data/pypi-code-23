# -*- encoding: UTF-8 -*-
from setuptools import setup, find_packages

"""
Userd to package
"""

VERSION = '0.1.1'

setup(name='vmaccess',
      version=VERSION,
      description="Initial triage for VM Access Control",
      long_description='just enjoy',
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python vm access control ssh sudo',
      author='danyachen',
      author_email='danyachen@ebay.com',
      url='https://github.corp.ebay.com/GPSCCOE/vmaccess',
      license='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'requests',
      ],
      entry_points={
          'console_scripts': [
              'vmaccess = access.access_rule:main'
          ]
      },
      )