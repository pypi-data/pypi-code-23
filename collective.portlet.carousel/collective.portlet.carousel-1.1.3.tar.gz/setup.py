# -*- coding: utf-8 -*-
"""Installer for the collective.portlet.carousel package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='collective.portlet.carousel',
    version='1.1.3',
    description="Carousel for collective.panels",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone portlets carousel panels',
    author='Bo Simonsen',
    author_email='bo@headnet.dk',
    url='https://pypi.python.org/pypi/collective.portlet.carousel',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages = ['collective', 'collective.portlet'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.app.portlets',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
