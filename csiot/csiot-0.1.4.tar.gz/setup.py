from __future__ import print_function
from setuptools import setup, find_packages
from subprocess import Popen, PIPE

version="0.1-4-g9906832"

version = '.'.join(version.split("-")[:-1])

if not version:
	print("Couldn't parse git version")
	exit(1)

print("Building csiot '%s'" % version)
setup(
		name="csiot",
		version=version,
		author="Kevin Morris",
		author_email="kevin.morris@codestruct.net",
		description="CSIoT Python SDK",
		url="https://codestruct.net",
		packages=find_packages()
)

