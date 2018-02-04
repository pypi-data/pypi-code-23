#!/usr/bin/env python

from setuptools import setup

setup(
	name = "wciwt",
	version = "0.0.0",
	description = "wciwt is a command line tool which makes it easier to find your favorite TV shows and movies in India. It hopes to support Netflix, Prime Video and Hotstar in the near future.",
	author = "Ajay",
	author_email = "ajaymkatte95@gmail.com",
	packages = ["wciwt"],
	download_url = "https://github.com/howdyauthors/wciwt",
	entry_points = {
		'console_scripts': [
			'wciwt = wciwt:wciwt'
		],
	},
	install_requires = ["requests"]
)