#!/usr/bin/env python

import os

from subprocess import check_call
from distutils.core import Command
from setuptools import setup

class DeployPypi(Command):
    description = "Deploy to pypi using twine"
    user_options = [
        ("repository=", "r", "Repository to upload to"),
    ]

    def initialize_options(self):
        self.repository = None

    def finalize_options(self):
        if not self.repository:
            raise RuntimeError("Need a repository to upload to! Run 'python setup.py upload_twine' for options.")

    def run(self):
        self.run_command("clean")
        self.run_command("sdist")

        if len(os.listdir("dist")) > 1:
            raise RuntimeError("More than one package in dist/ - only one can be present to upload! Delete the dist/ folder before running this command.")

        to_upload = os.path.join("dist", os.listdir("dist")[0])

        args = ["twine", "upload", "-r", self.repository, to_upload]

        self.execute(check_call,
            [args],
            msg="Uploading package to pypi")


setup(
    name="overlock",
    setup_requires = ["requests", "six", "pyyaml"],
    description = "Overlock client library for instrumenting code",
    keywords = ["iot", "overlock"],
    author = "Michael Boulton",
    author_email = "michael@overlock.io",

    cmdclass={
        "upload_twine": DeployPypi,
    },
)
