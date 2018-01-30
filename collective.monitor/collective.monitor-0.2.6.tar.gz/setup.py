# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.2.6'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='collective.monitor',
      version=version,
      description="Monitoring meta package for Zope/Plone installs",
      long_description=long_description,
      classifiers=[
          "Environment :: Web Environment",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
        ],
      keywords='Probe Plone Zope',
      author='Benoît Suttor',
      author_email='bsuttor@imio.be',
      url='https://github.com/collective/collective.monitor',
      license='gpl',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Zope2',
          'five.z2monitor',
          'Products.ZNagios',
          'munin.zope',
          'zc.z3monitor',
          'zc.monitorcache',
          'zc.monitorlogstats',
      ])
