#!/usr/bin/env python

from setuptools import setup

setup(
	name="testcli",
	version="0.1.0",
	description="testclitool",
	author="aynranddog",
	author_email="aynranddog@gmail.com",
	url="https://nadh.in",
	packages=["testcli"],
	download_url="https://github.com/aynranddog/asdf",
	license="MIT",
	entry_points={
		'console_scripts': [
			'testcli = testcli:run'
		],
	},
	classifiers=[],
	install_requires=["requests"],
	include_package_data=True
)