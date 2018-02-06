# coding: Latin-1
# Copyright © 2018 The Things Network
# Use of this source code is governed by the
# MIT license that can be found in the LICENSE file.

from setuptools import setup

setup(name="emmlej-dummy",
      version="0.0.3",
      description="Dummy Package for Testing",
      long_description = "Dummy package to test upload to Pypi with Travis",
      url = "https://github.com/emmlejeail/dummy-package",
      author="Emmanuelle Lejeail",
      author_email="manu.lejeail@gmail.com",
      license="MIT",
      packages=["src"],
      install_requires=[],
      zip_safe=False)
