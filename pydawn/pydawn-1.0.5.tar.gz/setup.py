from setuptools import setup, find_packages
import sys, os

version = '1.0.5'

setup(name='pydawn',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='palydawn',
      author='palydawn',
      author_email='palydawn@163.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'selenium', 'lxml', 'requests', 'matplotlib', 'numpy', 'burst_detection',# -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
