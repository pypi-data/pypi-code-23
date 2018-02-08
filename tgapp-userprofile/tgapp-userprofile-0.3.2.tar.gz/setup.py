# -*- coding: utf-8 -*-
import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires=[
    "TurboGears2 >= 2.3.0",
    "tgext.pluggable>=0.7.2",
    "tgapp-resetpassword",
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='tgapp-userprofile',
    version='0.3.2',
    description='Pluggable application for TurboGears2 which provides a basic user profile page with forms to allow users to edit their own profile or change their password',
    long_description=README,
    author='Mirko Darino, Alessandro Molina, Vincenzo Castiglia, Marco Bosio',
    author_email='mirko.darino@axant.it, alessandro.molina@axant.it, vincenzo.castiglia@axant.it, marco.bosio@axant.it',
    url='https://github.com/axant/tgapp',
    keywords='turbogears2.application',
    setup_requires=[],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    package_data={'tgapp.userprofile': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'userprofile': [
            ('**.py', 'python', None),
            ('templates/**.xhtml', 'kajiki', None),
            ('public/**', 'ignore', None)
    ]},

    entry_points="""
    """,
    dependency_links=[
        ],
    zip_safe=False
)
