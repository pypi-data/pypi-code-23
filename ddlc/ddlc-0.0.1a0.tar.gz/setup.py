#! /usr/bin/env python

descr = """Dynamic Dispatch Line Commands

Framework for creating and dispatching complex and dynamic line commands.

Please refer to the online documentation at
http://just-monika.club/ddlc/docs
"""

from setuptools import setup, find_packages
from ddlc.util import version

DISTNAME = 'ddlc'
DESCRIPTION = 'Framework for parsing complex line commands.'
LONG_DESCRIPTION = descr
MAINTAINER = 'Kira Evans'
MAINTAINER_EMAIL = 'contact@kne42.me'
URL = 'http://just-monika.club/ddlc'
LICENSE = 'Modified BSD'
DOWNLOAD_URL = 'https://github.com/just-monika/ddlc'
VERSION = version('ddlc/__init__.py')
PACKAGES = find_packages(exclude=['doc'])


if __name__ == '__main__':
    setup(
        name=DISTNAME,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        url=URL,
        license=LICENSE,
        download_url=DOWNLOAD_URL,
        version=VERSION,
        packages=PACKAGES
    )
