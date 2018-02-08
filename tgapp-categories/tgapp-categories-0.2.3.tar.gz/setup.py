# -*- coding: utf-8 -*-
import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires = [
    "TurboGears2 >= 2.3.9",
    "tgext.pluggable >= 0.7.1",
    'sprox',
    "filedepot",
    'kajiki',
]

testpkgs = [
    'WebTest >= 1.2.3',
    'nose',
    'coverage',
    'ming',
    'sqlalchemy',
    'zope.sqlalchemy',
    'repoze.who',
    'tw2.forms',
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='tgapp-categories',
    version='0.2.3',
    description='categories management system for web applications in turbogears2',
    long_description=README,
    author='Axant, Vincenzo Castilgia',
    author_email='vincenzo.castiglia@axant.it',
    url='https://github.com/axant/tgapp-categories',
    keywords='turbogears2.application',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    package_data={'tgappcategories': [
        'i18n/*/LC_MESSAGES/*.mo',
        'templates/*/*',
        'public/*/*'
    ]},
    message_extractors={'tgappcategories': [
            ('**.py', 'python', None),
            ('templates/**.xhtml', 'kajiki', None),
            ('public/**', 'ignore', None)
    ]},
    entry_points="""
    """,
    zip_safe=False,
    extras_require={
           'testing': testpkgs,
    },
)
