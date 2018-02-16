# -*- coding: utf-8 -*-
"""
This module contains the tool of cs.at.gipuzkoairekia
"""
import os
from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.txt')
    + '\n' )

setup(
    name='cs.at.gipuzkoairekia',
    version=version,
    description="An add-on for Plone to expose the contents of Gipuzkoa Irekia, an open government platform",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='',
    author='Mikel Larreategi',
    author_email='mlarreategi@codesyntax.com',
    url='https://github.com/codesyntax/cs.at.gipuzkoairekia',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['cs', 'cs.at'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'Plone <= 4.99',
        'Products.Archetypes',
        'archetypes.schemaextender',
        'five.globalrequest',
        'requests',
        'lxml',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.robotframework[debug]',
            'plone.api',
        ],
    },
    entry_points="""
    # -*- entry_points -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
    setup_requires=["PasteScript"],
    paster_plugins=["ZopeSkel"],
    )
