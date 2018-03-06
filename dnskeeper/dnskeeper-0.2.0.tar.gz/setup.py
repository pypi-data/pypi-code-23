#
# setup.py: setuptools control.
#

import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('dnskeeper/dnskeeper.py').read(),
    re.M
    ).group(1)

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    author = "William Forsyth",
    author_email = "william.forsyth@liferay.com",
    description = "Tool for managing DNS records in cloudflare and storing them locally in JSON.",
    entry_points = {
        "console_scripts": ['dnskeeper = dnskeeper.dnskeeper:main']
        },
    install_requires = [
        'CloudFlare',
        'tabulate'
    ],
    license = "BSD-2-Clause",
    long_description = long_descr,
    name = "dnskeeper",
    packages = ["dnskeeper"],
    url='https://github.com/liftedkilt/dnskeeper-cloudflare',
    version = version,
    )