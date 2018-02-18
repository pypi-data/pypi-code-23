#!/usr/bin/env python3
import sys

from fsforms import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


try:
    # those files are generated at build time
    readme = open('README.rst').read()
    changelog = open('CHANGELOG.rst').read()
except IOError as err:
    if 'upload' in sys.argv:
        print(("It seems that the README and/or the CHANGELOG have not been "
               "converted to reStructuredText markup. Please ensure that you "
               "are using 'make release' command to upload this package.\n\n"
               "Details: {}".format(err)),
              file=sys.stderr)
        sys.exit(1)
    readme = open('README.md').read()
    changelog = open('CHANGELOG.md').read()

setup(
    name='django-fsforms',
    version=__version__,
    description=(
        "A reusable Django application for rendering forms with "
        "Foundation for Sites."
    ),
    author='Jérôme Lebleu',
    author_email='jerome.lebleu@cliss21.org',
    url='https://forge.cliss21.org/cliss21/django-fsforms',
    packages=['fsforms'],
    include_package_data=True,
    install_requires=[],
    license="GNU AGPL-3",
    long_description=readme + '\n\n' + changelog,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)
