# -*- coding: utf-8 -*-

from os.path import dirname, join
from setuptools import setup


#
# Options
#

name = "pipcmd"

version = "0.1"

description = "Tool for installing and managing commands installed from PyPI"

try:
    long_description = open(join(dirname(__file__), "README.rst")).read()
except IOError:
    long_description = None

url = "https://github.com/wsanchez/pipcmd"

author = maintainer = "Wilfredo Sánchez Vega"
author_email = maintainer_email = "wsanchez@wsanchez.net"

license = "MIT"

platforms = ["all"]

classifiers = [
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Topic :: System :: Software Distribution",
    "Topic :: Utilities",
    "Operating System :: POSIX",
]

keywords = "PyPI pip"

scripts = ["bin/pipcmd"]


#
# Dependencies
#

python_requires = ">=2.7"

setup_requirements = []

install_requirements = [
    "pip",
    "virtualenv",
]

extras_requirements = {}


#
# Run setup
#

args = dict(
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    description=description,
    extras_require=extras_requirements,
    install_requires=install_requirements,
    keywords=keywords,
    license=license,
    long_description=long_description,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    name=name,
    platforms=platforms,
    python_requires=python_requires,
    scripts=scripts,
    setup_requires=setup_requirements,
    url=url,
    version=version,
)


def main():
    """
    Run setup.
    """
    setup(**args)


if __name__ == "__main__":
    main()
