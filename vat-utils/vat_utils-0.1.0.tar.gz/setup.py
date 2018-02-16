"""
setup.py
"""

from setuptools import find_packages, setup

###

NAME = 'vat_utils'
VERSION = '0.1.0'
PACKAGES = find_packages(where='src')
INSTALL_REQUIRES = ['boto3', 'jsonpointer']

AUTHOR = 'VAT Dev'
AUTHOR_EMAIL = 'vatdev@invalid.in'

###

if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        packages=PACKAGES,
        package_dir={"": "src"},
        install_requires=INSTALL_REQUIRES,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL
    )
