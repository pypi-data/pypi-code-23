import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "darfortie",
    version = "1.0.1",
    author = "Kenneth Galle",
    author_email = "ken.galle@rainshowers.org",
    description = "A utility that extends and simplifies using dar (Disk ARchive) for doing routine incremental backups.",
    keywords = "dar incremental backup",
    url = "https://github.com/kagalle/darfortie",
    packages=["darfortie"],
    entry_points={'console_scripts': ['darfortie = darfortie.darfortie_main:main']},
    long_description=read("README.rst"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Archiving :: Backup",
    ],
)
