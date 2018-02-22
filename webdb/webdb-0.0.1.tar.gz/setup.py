#!/usr/bin/python3

from setuptools import setup, find_packages
import sys
from os import path

if(sys.version_info.major != 3 ):
	raise SystemError("webdb requires python3")

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
	name = "webdb",
	version = "0.0.1",
	description = "Adapter for exposing databases to the web",
	long_description = long_description,
	url = "https://github.com/daknuett/webdb",
	author = "Daniel Knüttel",
	author_email = "daniel.knuettel@daknuett.eu",
	license = "AGPL v3",
	classifiers = ['Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU Affero General Public License v3',
		'Programming Language :: Python :: 3'],
	keywords = "database web json",
	install_requires = [
		"cherrypy"
	],
	packages = find_packages()
     )


