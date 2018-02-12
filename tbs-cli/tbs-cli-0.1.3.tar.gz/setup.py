import os
from setuptools import setup

NAME = "tbs-cli"
VERSION = os.getenv("TBS_CLI_VERSION")
REQUIRES = [
    "click == 6.7",
    "tbs-sdk >= 0.0.7",
    "colorama == 0.3.9"
]

setup(
    name=NAME,
    version=VERSION,
    description="IllumiDesk Command Line Tool",
    author=["John Griebel", "Nathaniel Compton"],
    author_email="jgriebel@3blades.io",
    url="https://github.com/IllumiDesk/python-cli-tools",
    download_url=f'https://github.com/IllumiDesk/python-cli-tools/archive/{VERSION}.tar.gz',
    keywords=["Illumidesk", "Data Science"],
    packages=["command_groups", "tbscli"],
    install_requires=REQUIRES,
    entry_points={'console_scripts': ["tbs=tbscli.tbs:main"]},
    include_package_data=True,
    license="BSD 3-clause"
)
